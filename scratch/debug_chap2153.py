import os
import sys
import time
import subprocess
from playwright.sync_api import sync_playwright

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
profile_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "browser_profile")
url = "https://www.novel543.com/0407603375/8096_2174.html"

cmd = [
    chrome_path,
    "--remote-debugging-port=9222",
    f"--user-data-dir={profile_dir}",
    "--no-first-run",
    "--no-default-browser-check",
    url
]
subprocess.Popen(cmd)
time.sleep(3)

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = b.contexts[0].pages[0]
    print("Page URL:", page.url)
    print("Page Title:", page.title())
    content_el = page.query_selector("div.chapter-content, div.content, #content")
    print("Content Element found?:", content_el is not None)
    if content_el:
        print("Content text length:", len(content_el.inner_text()))
        print("First 200 chars:\n", content_el.inner_text()[:200])
    else:
        print("Body text snippet:\n", page.evaluate("() => document.body.innerText.substring(0, 500)"))
    b.close()
