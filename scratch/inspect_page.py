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
    page.goto("https://www.novel543.com/0407603375/8096_2025_2.html", wait_until="domcontentloaded")
    print("Page 2 Title:", page.title())
    
    links = page.query_selector_all("a")
    for a in links:
        t = a.inner_text().strip()
        h = a.get_attribute("href")
        if any(w in t for w in ["上一章", "下一章"]):
            print(f"{t} -> {h}")
    b.close()
