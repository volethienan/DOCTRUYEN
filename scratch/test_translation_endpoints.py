import urllib.request
import urllib.parse
import json
import re
import sys

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

test_zh = "第2005章 倒霉的葉塵"

# 1. Google Translate Mobile (translate.google.com/m)
print("--- [1] Google Mobile (translate.google.com/m) ---")
try:
    url = "https://translate.google.com/m?sl=zh-CN&tl=vi&q=" + urllib.parse.quote(test_zh)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)"})
    with urllib.request.urlopen(req, timeout=5) as r:
        html = r.read().decode("utf-8")
        m = re.search(r'class="result-container">(.*?)</div>', html)
        if m:
            print("✓ Result:", m.group(1))
        else:
            print("! No result-container found, len:", len(html))
except Exception as e:
    print("✗ Error:", e)

# 2. MyMemory Translation API
print("\n--- [2] MyMemory API ---")
try:
    url = f"https://api.mymemory.translated.net/get?q={urllib.parse.quote(test_zh)}&langpair=zh|vi"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=5) as r:
        data = json.loads(r.read().decode("utf-8"))
        print("✓ Result:", data["responseData"]["translatedText"])
except Exception as e:
    print("✗ Error:", e)

# 3. Google Translate gtx with different referrer / headers
print("\n--- [3] Google gtx with alternative query ---")
try:
    url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=vi&dt=t&q={urllib.parse.quote(test_zh)}"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "AndroidTranslate/5.3.0.RC02.130475354-53000263 5.1 phone TRANSLATE_OPM5_TEST_1",
            "Accept": "*/*"
        }
    )
    with urllib.request.urlopen(req, timeout=5) as r:
        data = json.loads(r.read().decode("utf-8"))
        print("✓ Result:", "".join(p[0] for p in data[0] if p and p[0]))
except Exception as e:
    print("✗ Error:", e)

# 4. Check NINE_ROUTER_API_KEY
import os
print("\n--- [4] NINE_ROUTER_API_KEY ---")
api_key = os.environ.get("NINE_ROUTER_API_KEY")
print("Key exists:", bool(api_key))
if api_key:
    try:
        from openai import OpenAI
        client = OpenAI(
            base_url="https://api.nine-router.com/v1" if "nine-router" in api_key else "https://openrouter.ai/api/v1",
            api_key=api_key
        )
        print("Testing OpenAI client with key...")
    except Exception as e:
        print("Error with key:", e)
