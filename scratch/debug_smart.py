import sys
import os
import translators as ts
from deep_translator import GoogleTranslator, MyMemoryTranslator

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import database

c = database.get_chapter(2002)
paragraphs = c["content_zh"].split("\n")
chunk = "\n".join(paragraphs[:10])
print(f"Testing chunk length: {len(chunk)}")
print(f"Sample input:\n{chunk[:200]}\n")

print("--- Testing ts.translate_text with bing ---")
try:
    res = ts.translate_text(chunk, translator="bing", from_language="zh", to_language="vi")
    print("Bing succeeded! Result length:", len(res))
    print("Bing sample:\n", res[:300])
except Exception as e:
    print("Bing FAILED with exception:", type(e), e)
