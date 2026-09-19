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
for ch in [2036, 2037, 2118, 2193, 2215]:
    c.execute('SELECT content_vi FROM chapters WHERE chapter_num = ?', (ch,))
    text = c.fetchone()[0] or ''
    for m in re.finditer(r'[\u4e00-\u9fff]', text):
        s = max(0, m.start() - 30)
        e = min(len(text), m.end() + 30)
        ctx = text[s:e].replace('\n', ' ')
        print(f"Ch {ch}: [{m.group(0)}] -> ...{ctx}...")
