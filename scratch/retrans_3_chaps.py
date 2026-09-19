import sys
import os
sys.path.insert(0, os.path.abspath("."))
import sqlite3
import re
import translator
import database

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

conn = database.get_connection()
c = conn.cursor()

for ch in [2075, 2135, 2142]:
    c.execute("SELECT chapter_num, title_zh, content_zh, title_vi, content_vi FROM chapters WHERE chapter_num = ?", (ch,))
    row = c.fetchone()
    title_zh = row["title_zh"]
    content_zh = row["content_zh"]
    old_c_vi = row["content_vi"] or ""
    old_zh_count = len(re.findall(r'[\u4e00-\u9fff]', old_c_vi))
    
    print(f"\n--- Retranslating Chapter {ch}: {title_zh} (Old Chinese chars: {old_zh_count}) ---")
    new_title_vi, new_content_vi = translator.translate_chapter(title_zh, content_zh)
    new_zh_count = len(re.findall(r'[\u4e00-\u9fff]', new_content_vi))
    print(f"Result: {new_title_vi}")
    print(f"Old zh chars: {old_zh_count} -> New zh chars: {new_zh_count}")
    
    # Save to database
    c.execute("UPDATE chapters SET title_vi = ?, content_vi = ?, updated_at = CURRENT_TIMESTAMP WHERE chapter_num = ?", 
              (new_title_vi, new_content_vi, ch))
    conn.commit()
    print(f"Saved Chapter {ch} to database successfully.")

conn.close()
