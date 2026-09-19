import sys
import sqlite3
import re
from collections import Counter

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

conn = sqlite3.connect('novel.db')
c = conn.cursor()
c.execute('SELECT chapter_num, content_vi FROM chapters WHERE chapter_num >= 2000 ORDER BY chapter_num ASC')
rows = c.fetchall()

snippets = []
word_counter = Counter()

for chap_num, content_vi in rows:
    if not content_vi:
        continue
    for m in re.finditer(r'[\u4e00-\u9fff]+', content_vi):
        start = max(0, m.start() - 25)
        end = min(len(content_vi), m.end() + 25)
        word = m.group(0)
        word_counter[word] += 1
        ctx = content_vi[start:end].replace('\n', ' ')
        snippets.append((chap_num, word, ctx))

print(f"Total occurrences of Chinese in content_vi: {len(snippets)}")
print(f"Unique Chinese words/segments: {len(word_counter)}")
print("\n--- TOP WORDS ---")
for word, count in word_counter.most_common(50):
    print(f"{word}: {count}")

with open("scratch/all_chinese_snippets.txt", "w", encoding="utf-8") as f:
    for chap_num, word, ctx in snippets:
        f.write(f"Ch {chap_num} | [{word}] | ...{ctx}...\n")

print("\nWrote all snippets to scratch/all_chinese_snippets.txt")
