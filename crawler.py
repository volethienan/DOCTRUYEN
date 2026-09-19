import os
import sys
import re
import time
import random
import subprocess
import urllib.request
import json
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import database
import translator

BASE_URL = "https://www.novel543.com"
BOOK_ID = "0407603375"
TOC_URL = f"{BASE_URL}/{BOOK_ID}/dir"
PROFILE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "browser_profile")
CDP_URL = "http://127.0.0.1:9222"

def is_cdp_ready():
    try:
        with urllib.request.urlopen(f"{CDP_URL}/json/version", timeout=1) as r:
            return r.status == 200
    except Exception:
        return False

def launch_normal_browser():
    """Khởi chạy Chrome thật với cổng remote debugging"""
    if is_cdp_ready():
        return True

    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    browser_exe = chrome_path if os.path.exists(chrome_path) else edge_path

    if not os.path.exists(browser_exe):
        print(f"[X] Không tìm thấy file chạy trình duyệt tại: {browser_exe}")
        return False

    cmd = [
        browser_exe,
        "--remote-debugging-port=9222",
        f"--user-data-dir={PROFILE_DIR}",
        "--no-first-run",
        "--no-default-browser-check",
        TOC_URL
    ]
    print(f"[*] Đang khởi chạy trình duyệt thật: {browser_exe}")
    subprocess.Popen(cmd)

    for _ in range(30):
        if is_cdp_ready():
            return True
        time.sleep(0.5)

    return False

def parse_chapter_number(title: str, default_num: int = 0) -> int:
    """Trích xuất số thứ tự chương từ tiêu đề"""
    match = re.search(r"第\s*(\d+)\s*章", title)
    if match:
        return int(match.group(1))
    
    match2 = re.search(r"(\d+)", title)
    if match2:
        return int(match2.group(1))
        
    return default_num

def check_and_handle_cloudflare(page, timeout_sec: int = 300) -> bool:
    """
    Kiểm tra xem trang có bị Cloudflare chặn không.
    Nếu bị chặn, hệ thống sẽ tạm dừng và chờ bạn bấm xác nhận trên Chrome.
    """
    try:
        title = page.title()
        body_sample = page.evaluate("() => document.body ? document.body.innerText.substring(0, 400) : ''")
    except Exception:
        return True

    if "Just a moment" in title or "Security verification" in body_sample or "Cloudflare" in title:
        print("\n" + "!"*70)
        print("[⚠️ PHÁT HIỆN CLOUDFLARE BẬT LẠI GIỮA CHỪNG]")
        print(">>> Cloudflare vừa yêu cầu xác thực người thật trên trình duyệt.")
        print(">>> Vui lòng chuyển sang cửa sổ Chrome và bấm tick xác nhận.")
        print(">>> Crawler đang TỰ ĐỘNG CHỜ bạn xác thực xong để tiếp tục...")
        print("!"*70 + "\n")

        start_t = time.time()
        while time.time() - start_t < timeout_sec:
            time.sleep(2)
            try:
                cur_title = page.title()
                if "Just a moment" not in cur_title and "Cloudflare" not in cur_title:
                    print(f"[✓] Xác thực thành công! Đang tiếp tục cào truyện...\n")
                    time.sleep(1)
                    return True
            except Exception:
                pass
        print("[X] Hết thời gian chờ xác minh Cloudflare.")
        return False

    return True

def get_chapter_list(page, min_chapter: int = 2000):
    """Lấy danh sách các chương từ min_chapter trở đi"""
    if not page.url.startswith(TOC_URL):
        page.goto(TOC_URL, wait_until="domcontentloaded", timeout=60000)

    # Kiểm tra Cloudflare
    check_and_handle_cloudflare(page)

    # Lưu thông tin truyện
    try:
        book_title_el = page.query_selector("h1") or page.query_selector(".title")
        book_title = book_title_el.inner_text().strip() if book_title_el else "蛇仙：開局吞噬仙帝"
        database.save_novel_info(
            book_id=BOOK_ID,
            title_zh=book_title,
            title_vi="Xà Tiên: Khai Cục Thôn Phệ Tiên Đế",
            author_zh="咯比猴",
            author_vi="Cạc Tỷ Hầu",
            source_url=TOC_URL
        )
    except Exception:
        pass

    elements = page.query_selector_all("div.chaplist ul li a, div.chaplist a, ul.chapter-list a")
    if not elements:
        elements = page.query_selector_all(f"a[href*='/{BOOK_ID}/']")

    print(f"[i] Tổng số link chương tìm thấy trên trang mục lục: {len(elements)}")
    
    chapters = []
    seen_urls = set()
    
    for el in elements:
        try:
            href = el.get_attribute("href")
            if not href or href in ("#", "javascript:void(0);"):
                continue
            if href.endswith("/dir") or href.endswith(f"/{BOOK_ID}/"):
                continue
                
            full_url = urljoin(BASE_URL, href)
            if full_url in seen_urls:
                continue
            seen_urls.add(full_url)
            
            title = el.inner_text().strip()
            chap_num = parse_chapter_number(title)
            
            if chap_num >= min_chapter:
                chapters.append({
                    "chapter_num": chap_num,
                    "title_zh": title,
                    "url": full_url
                })
        except Exception:
            continue
            
    chapters.sort(key=lambda x: x["chapter_num"])
    print(f"[✓] Đã lọc được {len(chapters)} chương từ chương {min_chapter} trở đi.")
    return chapters

def extract_chapter_content(page, url: str, retries: int = 2) -> tuple[str, str]:
    """
    Truy cập trang chương và trích xuất tiêu đề cùng toàn bộ nội dung.
    Tự động ghép nối các trang con 1/2 và 2/2 thành 1 chương duy nhất.
    Có cơ chế tự động xử lý khi dính Cloudflare giữa chừng.
    """
    filename = url.split("/")[-1].split("?")[0].replace(".html", "")
    base_stem = re.sub(r"_\d+$", "", filename) if re.search(r"_\d+_\d+$", filename) else filename
    
    full_content = []
    chapter_title = ""
    current_url = url
    page_num = 1
    
    while current_url:
        page.goto(current_url, wait_until="domcontentloaded", timeout=35000)
        
        # Nếu bị dính Cloudflare trên trang này, tạm dừng chờ người dùng giải
        if not check_and_handle_cloudflare(page):
            return "", ""
            
        data = page.evaluate("""(baseStem) => {
            const titleEl = document.querySelector('h1.title, h1');
            const contentEl = document.querySelector('div.chapter-content, div.content, #content');
            
            let text = '';
            if (contentEl) {
                const paras = Array.from(contentEl.querySelectorAll('p'));
                if (paras.length > 0) {
                    text = paras.map(p => p.innerText.trim()).filter(Boolean).join('\\n\\n');
                } else {
                    text = contentEl.innerText.trim();
                }
            }

            // Tìm link sang trang tiếp theo của cùng chương (ví dụ 8096_2025_2.html)
            let nextPartUrl = null;
            const targetPattern = baseStem + '_';
            const links = Array.from(document.querySelectorAll('a'));
            for (const a of links) {
                const href = a.getAttribute('href') || '';
                if (href.includes(targetPattern)) {
                    nextPartUrl = a.href;
                    break;
                }
            }

            return {
                title: titleEl ? titleEl.innerText.trim() : '',
                content: text,
                nextPartUrl: nextPartUrl
            };
        }""", base_stem)
        
        # Nếu vẫn không có nội dung và trang có dấu hiệu Cloudflare, thử reload lại
        if not data["content"]:
            check_and_handle_cloudflare(page)
            page.reload(wait_until="domcontentloaded", timeout=30000)
            data = page.evaluate("""(baseStem) => {
                const titleEl = document.querySelector('h1.title, h1');
                const contentEl = document.querySelector('div.chapter-content, div.content, #content');
                let text = '';
                if (contentEl) {
                    const paras = Array.from(contentEl.querySelectorAll('p'));
                    text = paras.length > 0 ? paras.map(p => p.innerText.trim()).filter(Boolean).join('\\n\\n') : contentEl.innerText.trim();
                }
                return {
                    title: titleEl ? titleEl.innerText.trim() : '',
                    content: text,
                    nextPartUrl: null
                };
            }""", base_stem)
        
        if not chapter_title and data["title"]:
            raw_title = data["title"]
            chapter_title = re.sub(r"[\(（]\s*\d+\s*/\s*\d+\s*[\)）]", "", raw_title).strip()
            
        if data["content"]:
            cleaned_lines = []
            for line in data["content"].split("\n"):
                s = line.strip()
                if s and not any(ad in s.lower() for ad in ["novel543", "稷下書院", "無廣告", "点击下载", "本章完"]):
                    cleaned_lines.append(s)
            full_content.append("\n\n".join(cleaned_lines))
            
        current_url = data["nextPartUrl"]
        if current_url:
            page_num += 1
            
    final_content = "\n\n".join(full_content)
    return chapter_title, final_content

def crawl_and_translate(min_chapter: int = 2000, max_chapters: int = 300):
    """
    Hàm chính cào và dịch truyện từ min_chapter đến chương mới nhất.
    """
    database.init_db()
    
    print("="*70)
    print(f" KHỞI ĐỘNG CRAWLER TRUYỆN NOVEL543 (TỪ CHƯƠNG {min_chapter})")
    print("="*70)
    
    launched = launch_normal_browser()
    if not launched:
        print("[X] Không thể kết nối tới trình duyệt. Vui lòng thử lại!")
        return

    print("\n" + "="*70)
    print(">>> [TRÌNH DUYỆT THẬT ĐÃ SẴN SÀNG]")
    print(">>> Hãy nhìn vào cửa sổ Chrome đã mở.")
    print(">>> Khi trang đã hiển thị danh sách chương của truyện,")
    print(">>> hãy quay lại đây và nhấn ENTER để bắt đầu cào tự động!")
    print("="*70 + "\n")
    
    try:
        input("--> Nhấn ENTER sau khi đã thấy danh sách chương truyện: ")
    except Exception:
        time.sleep(3)

    with sync_playwright() as p:
        print("[*] Đang kết nối tới trình duyệt thật qua CDP...")
        browser = p.chromium.connect_over_cdp(CDP_URL)
        context = browser.contexts[0]
        
        page = None
        for pg in context.pages:
            if "novel543" in pg.url:
                page = pg
                break
        if not page:
            page = context.pages[0] if context.pages else context.new_page()

        chapter_list = get_chapter_list(page, min_chapter=min_chapter)
        if not chapter_list:
            print("[X] Chưa tìm thấy danh sách chương. Vui lòng đảm bảo bạn đã vào đúng trang mục lục!")
            browser.close()
            return
            
        print(f"\n[*] Bắt đầu xử lý {len(chapter_list)} chương...")
        
        count = 0
        for item in chapter_list:
            if max_chapters and count >= max_chapters:
                print(f"[i] Đã đạt giới hạn {max_chapters} chương cho lượt chạy này.")
                break
                
            chap_num = item["chapter_num"]
            chap_url = item["url"]
            chap_title_zh = item["title_zh"]
            
            # Kiểm tra xem chương đã hoàn thành và có nội dung tiếng Việt chưa
            existing = database.get_chapter(chap_num)
            if existing and existing["status"] == "completed" and existing["content_vi"] and len(existing["content_vi"]) > 100:
                continue
                
            print(f"\n--> [Chương {chap_num}] Đang cào: {chap_title_zh}")
            
            try:
                # Cào nội dung (ghép cả trang 1/2 và 2/2)
                title_zh, content_zh = extract_chapter_content(page, chap_url)
                if not title_zh:
                    title_zh = chap_title_zh
                if not content_zh:
                    print(f"    [!] Cảnh báo: Không lấy được nội dung chương {chap_num}, tạm dừng thử lại...")
                    # Cho thêm 1 cơ hội giải Cloudflare
                    check_and_handle_cloudflare(page)
                    title_zh, content_zh = extract_chapter_content(page, chap_url)
                    
                if not content_zh:
                    print(f"    [X] Vẫn không lấy được nội dung chương {chap_num}. Bỏ qua...")
                    database.upsert_chapter(chap_num, title_zh, chap_url, status="error")
                    continue
                    
                # Lưu bản gốc tiếng Trung
                database.upsert_chapter(chap_num, title_zh, chap_url, content_zh=content_zh, status="crawled")
                print(f"    [✓] Đã cào xong ({len(content_zh)} ký tự, ghép đủ các trang con). Đang dịch POST...")
                
                # Dịch sang tiếng Việt bằng HTTP POST không bao giờ bị 400 Bad Request
                title_vi, content_vi = translator.translate_chapter(title_zh, content_zh)
                database.update_chapter_translation(chap_num, title_vi, content_vi, status="completed")
                print(f"    [✓] Dịch hoàn tất: {title_vi}")
                print(f"    [✓] Đã lưu vào CSDL (novel.db)")
                
                count += 1
                # Giãn cách an toàn ngẫu nhiên để Cloudflare không kích hoạt lại
                delay = random.uniform(1.2, 2.2)
                time.sleep(delay)
                
            except Exception as e:
                print(f"    [X] Lỗi khi xử lý chương {chap_num}: {e}")
                time.sleep(2)

        print("\n" + "="*70)
        print(f"[HOÀN TẤT] Lượt này đã cào & dịch thêm được: {count} chương.")
        stats = database.get_stats()
        print(f"Thống kê CSDL hiện tại: {stats['completed']}/{stats['total']} chương đã hoàn chỉnh!")
        print("="*70)

if __name__ == "__main__":
    min_chap = 2000
    if len(sys.argv) > 1:
        try:
            min_chap = int(sys.argv[1])
        except ValueError:
            pass
    crawl_and_translate(min_chapter=min_chap)
