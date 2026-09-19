import sys
import re
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def extract_full_chapter(page, url: str):
    # Lấy chính xác tên file gốc của chương, ví dụ "8096_2025"
    filename = url.split("/")[-1].split("?")[0].replace(".html", "")
    # Nếu url ban đầu đã là trang con (ví dụ 8096_2025_2), đưa về gốc
    base_stem = re.sub(r"_\d+$", "", filename) if re.search(r"_\d+_\d+$", filename) else filename
    print(f"Base chapter stem: {base_stem}")

    full_content = []
    chapter_title = ""
    current_url = url
    page_num = 1

    while current_url:
        print(f"  -> Đang cào trang {page_num}: {current_url}")
        page.goto(current_url, wait_until="domcontentloaded", timeout=30000)

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

        if not chapter_title and data["title"]:
            raw_title = data["title"]
            # Xóa các hậu tố (1/2), (2/2)
            chapter_title = re.sub(r"[\(（]\s*\d+\s*/\s*\d+\s*[\)）]", "", raw_title).strip()

        if data["content"]:
            # Lọc bỏ quảng cáo
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
    print(f"[✓] Đã cào & ghép xong {page_num} trang của chương!")
    print(f"[✓] Tiêu đề sạch: {chapter_title}")
    print(f"[✓] Tổng ký tự: {len(final_content)}")
    return chapter_title, final_content

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = b.contexts[0].pages[0]
    t, c = extract_full_chapter(page, "https://www.novel543.com/0407603375/8096_2025.html")
    b.close()
