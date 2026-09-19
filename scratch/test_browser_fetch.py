import sys
from playwright.sync_api import sync_playwright

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = b.contexts[0].pages[0]
    
    js_code = """async () => {
        try {
            const url = 'https://translate.googleapis.com/translate_a/single?client=gtx&sl=zh-CN&tl=vi&dt=t&q=' + encodeURIComponent('第2005章 倒霉的葉塵');
            const resp = await fetch(url);
            if (!resp.ok) return 'HTTP ' + resp.status;
            const data = await resp.json();
            return data[0][0][0];
        } catch(e) {
            return 'ERROR: ' + e.message;
        }
    }"""
    
    res = page.evaluate(js_code)
    print("Fetch result from Chrome:", res)
    b.close()
