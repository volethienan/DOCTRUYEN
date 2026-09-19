import sys
from playwright.sync_api import sync_playwright

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, channel="chrome")
    page = browser.new_page(viewport={"width": 1300, "height": 900})
    page.goto("http://localhost:8088")
    page.wait_for_timeout(1000)

    # 1. Check initial order
    c_asc = page.eval_on_selector_all(".chapter-card", "els => els.slice(0, 5).map(e => e.dataset.chapNum)")
    print("1. Initial order (asc):", c_asc)

    # 2. Click Sort Descending button
    page.click("#btn-sort-desc")
    page.wait_for_timeout(400)
    c_desc = page.eval_on_selector_all(".chapter-card", "els => els.slice(0, 5).map(e => e.dataset.chapNum)")
    print("2. After click #btn-sort-desc (Mới ➔ Cũ):", c_desc)

    # 3. Click Sort Ascending button
    page.click("#btn-sort-asc")
    page.wait_for_timeout(400)
    c_asc2 = page.eval_on_selector_all(".chapter-card", "els => els.slice(0, 5).map(e => e.dataset.chapNum)")
    print("3. After click #btn-sort-asc (Cũ ➔ Mới):", c_asc2)

    # 4. Range tab
    page.click(".range-tab:has-text('2200 - 2223')")
    page.wait_for_timeout(400)
    visible_count = page.eval_on_selector_all(".chapter-card:not([style*='display: none'])", "els => els.length")
    print("4. Visible count for 2200 - 2223 range:", visible_count)

    # 5. Take screenshot
    page.click(".range-tab:has-text('Tất cả')")
    page.wait_for_timeout(400)
    page.locator("#chapters-section").scroll_into_view_if_needed()
    page.wait_for_timeout(500)
    page.screenshot(path="scratch/new_toc_design.png")
    print("5. Saved screenshot to scratch/new_toc_design.png")

    browser.close()
