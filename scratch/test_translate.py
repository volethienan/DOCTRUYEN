import urllib.parse
import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

def translate_zh_to_vi(text: str) -> str:
    if not text.strip():
        return ""
    # Using Google Translate free endpoint
    url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=zh-CN&tl=vi&dt=t&q=" + urllib.parse.quote(text)
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    )
    with urllib.request.urlopen(req, timeout=10) as response:
        data = json.loads(response.read().decode("utf-8"))
        result = "".join([part[0] for part in data[0] if part[0]])
        return result

test_text = "第2000章 蛇仙降世，开局吞噬仙帝！天地色变。"
translated = translate_zh_to_vi(test_text)
print("Original:", test_text)
print("Translated:", translated)
