import sqlite3
import re
import sys

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

conn = sqlite3.connect('novel.db')
c = conn.cursor()
c.execute("SELECT chapter_num, title_vi, content_vi FROM chapters WHERE chapter_num >= 2000")
rows = c.fetchall()

found = 0
for ch, title_vi, content_vi in rows:
    text = (title_vi or "") + "\n" + (content_vi or "")
    for m in re.finditer(r'可是', text):
        found += 1
        s = max(0, m.start() - 40)
        e = min(len(text), m.end() + 40)
        ctx = text[s:e].replace('\n', ' ')
        print(f"Ch {ch}: ...{ctx}...")

print(f"\nTotal occurrences of 可是: {found}")
