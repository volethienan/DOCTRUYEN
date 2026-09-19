import subprocess
import time
import os
import sys
import urllib.request
import json
from playwright.sync_api import sync_playwright

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
BROWSER_EXE = CHROME_PATH if os.path.exists(CHROME_PATH) else EDGE_PATH
PROFILE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cdp_profile")

def is_cdp_ready():
    try:
        with urllib.request.urlopen("http://127.0.0.1:9222/json/version", timeout=1) as r:
            return r.status == 200
    except Exception:
        return False

print("[1] Kiểm tra hoặc khởi chạy Chrome bình thường qua Remote Debugging Port...")
if not is_cdp_ready():
    cmd = [
        BROWSER_EXE,
        "--remote-debugging-port=9222",
        f"--user-data-dir={PROFILE_DIR}",
        "--no-first-run",
        "--no-default-browser-check",
        "https://www.google.com"
    ]
    subprocess.Popen(cmd)
    for _ in range(20):
        if is_cdp_ready():
            break
        time.sleep(0.5)

print("[2] CDP đã sẵn sàng. Kết nối qua Playwright CDP...")
with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    context = browser.contexts[0]
    page = context.pages[0] if context.pages else context.new_page()
    print("Page title:", page.title())
    print("navigator.webdriver is:", page.evaluate("navigator.webdriver"))
    browser.close()
    print("[✓] Hoàn tất thử nghiệm CDP!")
