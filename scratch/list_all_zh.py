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
c.execute("SELECT chapter_num, title_vi, content_vi FROM chapters WHERE chapter_num >= 2000 ORDER BY chapter_num ASC")
rows = c.fetchall()

words_dict = {}

for chap_num, title_vi, content_vi in rows:
    text = (title_vi or "") + "\n" + (content_vi or "")
    for m in re.finditer(r'[\u4e00-\u9fff]+', text):
        w = m.group(0)
        start = max(0, m.start() - 25)
        end = min(len(text), m.end() + 25)
        ctx = text[start:end].replace('\n', ' ')
        if w not in words_dict:
            words_dict[w] = []
        words_dict[w].append((chap_num, ctx))

print(f"Total unique Chinese phrases: {len(words_dict)}")
# Sort by frequency
sorted_words = sorted(words_dict.items(), key=lambda x: len(x[1]), reverse=True)
for w, occurrences in sorted_words:
    print(f"'{w}': {len(occurrences)} times (e.g. Ch {occurrences[0][0]}: ...{occurrences[0][1]}...)")
