import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import database

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

conn = database.get_connection()
cursor = conn.cursor()

print("="*60)
print("             BÁO CÁO KIỂM TRA CƠ SỞ DỮ LIỆU NOVEL.DB")
print("="*60)

stats = database.get_stats()
print(f"Tổng số chương trong DB: {stats['total']}")
print(f"Số chương hoàn thành:   {stats['completed']}")
print(f"Dải chương hiện có:      Chương {stats['min_chapter']} -> Chương {stats['max_chapter']}")

# Kiểm tra phân bố trạng thái
cursor.execute("SELECT status, COUNT(*) FROM chapters GROUP BY status")
status_counts = dict(cursor.fetchall())
print(f"Phân bố trạng thái:      {status_counts}")

# Kiểm tra các chương có vấn đề về nội dung
cursor.execute("SELECT chapter_num, title_zh, title_vi, length(content_zh), length(content_vi), status FROM chapters WHERE length(content_vi) < 200 OR content_vi IS NULL")
problem_chaps = cursor.fetchall()
print(f"\nSố chương thiếu/lỗi nội dung dịch (< 200 ký tự): {len(problem_chaps)}")
if problem_chaps:
    for c in problem_chaps[:10]:
        print(f"  - Chương {c[0]}: {c[1]} | Status: {c[5]} | Dài ZH: {c[3]} | Dài VI: {c[4]}")

# Thống kê độ dài trung bình của các chương
cursor.execute("SELECT AVG(length(content_zh)), AVG(length(content_vi)), MIN(length(content_vi)), MAX(length(content_vi)) FROM chapters WHERE status = 'completed'")
avg_zh, avg_vi, min_vi, max_vi = cursor.fetchone()
print(f"\nĐộ dài trung bình bản gốc tiếng Trung: {int(avg_zh or 0)} ký tự")
print(f"Độ dài trung bình bản dịch tiếng Việt: {int(avg_vi or 0)} ký tự")
print(f"Độ dài ngắn nhất / dài nhất:          {min_vi} / {max_vi} ký tự")

print("\n" + "-"*60)
print("     TRÍCH XUẤT MẪU BẢN DỊCH Ở CÁC GIAI ĐOẠN KHÁC NHAU")
print("-"*60)

sample_chap_nums = [2005, 2100, 2153, 2200, stats['max_chapter']]
for num in sample_chap_nums:
    cursor.execute("SELECT chapter_num, title_zh, title_vi, content_zh, content_vi FROM chapters WHERE chapter_num = ?", (num,))
    row = cursor.fetchone()
    if not row:
        continue
    c_num, t_zh, t_vi, c_zh, c_vi = row
    print(f"\n[★] CHƯƠNG {c_num}")
    print(f"  Tiêu đề gốc : {t_zh}")
    print(f"  Tiêu đề dịch: {t_vi}")
    print(f"  Độ dài gốc  : {len(c_zh or '')} ký tự")
    print(f"  Độ dài dịch : {len(c_vi or '')} ký tự")
    print("  Đoạn trích đầu bản dịch tiếng Việt:")
    sample_lines = [line.strip() for line in (c_vi or '').split('\n') if line.strip()][:3]
    for line in sample_lines:
        print(f"    > {line}")

conn.close()
