import os
import sys
import re
import translators as ts

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import database

c = database.get_chapter(2005)
print("Title ZH:", c["title_zh"])
print("Content ZH length:", len(c["content_zh"]))

# Dịch tiêu đề bằng Bing
t_vi = ts.translate_text(c["title_zh"], translator="bing", from_language="zh", to_language="vi")
print("Title VI:", t_vi)

# Dịch 3 đoạn đầu của nội dung
first_paragraphs = "\n\n".join(c["content_zh"].split("\n\n")[:3])
c_vi = ts.translate_text(first_paragraphs, translator="bing", from_language="zh", to_language="vi")
print("\nContent VI (3 đoạn đầu):\n", c_vi)
