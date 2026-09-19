import sys
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from deep_translator import GoogleTranslator, MyMemoryTranslator

test_text = "第2005章 倒霉的葉塵\n\n穩定的世界是無法被吞噬掉的，這隻說明，此界早已到了崩塌的邊緣。"

print("--- GoogleTranslator ---")
try:
    g_res = GoogleTranslator(source='auto', target='vi').translate(test_text)
    print("Google result:\n", g_res)
except Exception as e:
    print("Google error:", e)

print("\n--- MyMemoryTranslator ---")
try:
    m_res = MyMemoryTranslator(source='zh-CN', target='vi').translate("第2005章 倒霉的葉塵")
    print("MyMemory result:\n", m_res)
except Exception as e:
    print("MyMemory error:", e)
