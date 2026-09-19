import sys
import time
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import database
import translator

def is_mostly_chinese(text: str) -> bool:
    if not text:
        return True
    zh_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    return zh_chars / len(text) > 0.25

def translate_single_chapter(row_data: dict, completed_counter: list, total_count: int, lock: threading.Lock):
    chap_num = row_data["chapter_num"]
    title_zh = row_data["title_zh"]
    content_zh = row_data["content_zh"]

    with lock:
        print(f"[>] Đang dịch Chương {chap_num}: {title_zh} ({len(content_zh)} ký tự gốc)...", flush=True)

    t0 = time.time()
    try:
        title_vi, content_vi = translator.translate_chapter(title_zh, content_zh)

        # Kiểm tra nếu còn nhiều tiếng Trung thì thử lại 1 lần
        if is_mostly_chinese(content_vi):
            with lock:
                print(f"  [!] Cảnh báo: Chương {chap_num} còn sót tiếng Trung, thử dịch lại...", flush=True)
            time.sleep(1)
            title_vi, content_vi = translator.translate_chapter(title_zh, content_zh)

        # Lưu ngay vào CSDL
        database.update_chapter_translation(chap_num, title_vi, content_vi, status="completed")
        dt = time.time() - t0

        with lock:
            completed_counter[0] += 1
            print(f"  [✓] [{completed_counter[0]}/{total_count}] Chương {chap_num}: {title_vi} ({len(content_vi)} ký tự TV, {dt:.1f}s)", flush=True)

        return (chap_num, True, None)

    except Exception as e:
        with lock:
            print(f"  [X] Lỗi khi dịch chương {chap_num}: {e}", flush=True)
        return (chap_num, False, str(e))

def retranslate_missing_chapters(start_chap: int = 2000, max_count: int = None, workers: int = 3):
    """
    Tự động quét và dịch lại tất cả các chương trong DB có nội dung tiếng Việt bị lỗi hoặc chưa dịch.
    Đọc trực tiếp nội dung gốc tiếng Trung đã có sẵn trong DB, không cần mở trình duyệt.
    Hỗ trợ xử lý song song đa luồng (multi-threading) an toàn và nhanh chóng.
    """
    database.init_db()
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT chapter_num, title_zh, title_vi, content_zh, content_vi 
        FROM chapters 
        WHERE chapter_num >= ? 
        ORDER BY chapter_num ASC
    """, (start_chap,))
    rows = cursor.fetchall()
    conn.close()

    # Lọc các chương cần dịch
    need_translation = []
    for r in rows:
        c_vi = r["content_vi"] or ""
        t_vi = r["title_vi"] or ""
        c_zh = r["content_zh"] or ""

        if not c_zh or len(c_zh) < 100:
            continue

        if not c_vi or is_mostly_chinese(c_vi) or is_mostly_chinese(t_vi):
            need_translation.append(dict(r))

    print("=" * 75)
    print(f" TIẾN TRÌNH DỊCH THUẬT TIẾNG VIỆT TỰ ĐỘNG CHO CÁC CHƯƠNG TRONG DB")
    print(f" - Tổng số chương cần dịch: {len(need_translation)} chương")
    print(f" - Số luồng song song: {workers} workers")
    print("=" * 75, flush=True)

    if not need_translation:
        print("[✓] Toàn bộ các chương trong CSDL đều đã được dịch sang tiếng Việt hoàn chỉnh!")
        return

    if max_count:
        need_translation = need_translation[:max_count]
        print(f"[i] Giới hạn dịch: {len(need_translation)} chương trong phiên này.\n", flush=True)

    total_to_process = len(need_translation)
    completed_counter = [0]
    lock = threading.Lock()

    start_time = time.time()

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [
            executor.submit(translate_single_chapter, r, completed_counter, total_to_process, lock)
            for r in need_translation
        ]
        for f in as_completed(futures):
            _ = f.result()

    elapsed = time.time() - start_time
    print("\n" + "=" * 75)
    print(f" [HOÀN TẤT] Đã dịch xong {completed_counter[0]}/{total_to_process} chương trong {elapsed/60:.1f} phút!")
    print("=" * 75, flush=True)

if __name__ == "__main__":
    start = 2000
    limit = None
    workers = 3
    if len(sys.argv) > 1:
        try:
            start = int(sys.argv[1])
        except ValueError:
            pass
    if len(sys.argv) > 2:
        try:
            limit = int(sys.argv[2])
        except ValueError:
            pass
    if len(sys.argv) > 3:
        try:
            workers = int(sys.argv[3])
        except ValueError:
            pass
    retranslate_missing_chapters(start_chap=start, max_count=limit, workers=workers)
