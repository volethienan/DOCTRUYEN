import urllib.parse
import urllib.request
import json
import sys

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def translate_post(text: str) -> str:
    url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=zh-CN&tl=vi&dt=t"
    data = urllib.parse.urlencode({"q": text}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    )
    with urllib.request.urlopen(req, timeout=12) as response:
        res = json.loads(response.read().decode("utf-8"))
        result = "".join(p[0] for p in res[0] if p and p[0])
        return result

# Test với văn bản dài 5000 ký tự (tương đương cả 2 trang của chương 2005)
sample = (
    "第2005章 倒霉的葉塵\n\n"
    "浩瀚无垠的仙界苍穹之上，亿万星辰突然同时黯淡。\n\n"
    "一头浑身漆黑、鳞片泛着森冷幽光的远古巨蛇破空而出，遮天蔽日。它的双瞳犹如两轮猩红血月，俯瞰着下方巍峨耸立的太初神殿。\n\n"
    "「这……这是何等凶煞的远古妖蛇？！」太初仙帝身披九龙帝袍，惊怒交加，周身帝威如滔天骇浪般席卷开来。\n\n"
    "「仙帝？在吾的吞噬法则之下，万道皆为血食！」\n\n"
) * 10

translated = translate_post(sample)
print("Original length:", len(sample))
print("Translated length:", len(translated))
print("First 200 chars:\n", translated[:200])
