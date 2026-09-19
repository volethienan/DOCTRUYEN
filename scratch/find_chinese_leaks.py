import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import re
from collections import Counter
import database

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

conn = database.get_connection()
c = conn.cursor()
c.execute("SELECT chapter_num, title_vi, content_vi FROM chapters WHERE chapter_num >= 2000 ORDER BY chapter_num ASC")
rows = c.fetchall()
conn.close()

chinese_char_regex = re.compile(r'[\u4e00-\u9fff]+')
all_leaks = Counter()
chaps_with_leaks = {}

for r in rows:
    ch = r["chapter_num"]
    cv = r["content_vi"] or ""
    tv = r["title_vi"] or ""
    
    matches = chinese_char_regex.findall(cv) + chinese_char_regex.findall(tv)
    if matches:
        chaps_with_leaks[ch] = matches
        for m in matches:
            all_leaks[m] += 1

total_words = sum(all_leaks.values())
print("===========================================================================")
print(f" TỔNG KẾT RÀ SOÁT CHỮ TIẾNG TRUNG BỊ SÓT TRONG BẢN DỊCH TIẾNG VIỆT")
print(f" - Tổng số lần xuất hiện chữ Hán: {total_words}")
print(f" - Số lượng từ/cụm chữ Hán khác nhau: {len(all_leaks)}")
print(f" - Số chương có sót chữ Hán: {len(chaps_with_leaks)}/{len(rows)} chương")
print("===========================================================================")

print("\nDanh sách các từ/cụm chữ Hán xuất hiện nhiều nhất:")
for word, count in all_leaks.most_common(60):
    print(f"   '{word}': {count} lần")

# Samples with context
print("\n--- MỘT SỐ VÍ DỤ NGỮ CẢNH BỊ SÓT ---")
sample_count = 0
for r in rows:
    ch = r["chapter_num"]
    cv = r["content_vi"] or ""
    matches = chinese_char_regex.finditer(cv)
    for m in matches:
        word = m.group()
        start = max(0, m.start() - 25)
        end = min(len(cv), m.end() + 25)
        snippet = cv[start:end].replace("\n", " ")
        print(f"Ch {ch}: ...{snippet}...")
        sample_count += 1
        if sample_count >= 10:
            break
    if sample_count >= 10:
        break
