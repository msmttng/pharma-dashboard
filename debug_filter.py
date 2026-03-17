from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto('http://127.0.0.1:8080/index.html')
    page.evaluate("filterItems('pending')")
    
    handles = page.query_selector_all("tbody tr")
    for i, row in enumerate(handles[:30]):
        badge = row.query_selector(".status-badge")
        t = badge.text_content().strip() if badge else "None"
        display = row.evaluate("el => el.style.display")
        eval_pending = page.evaluate("(t) => t.includes('調達中') || t.includes('入荷未定') || t.includes('受注辞退') || t.includes('欠品') || t.includes('未納') || t.includes('未定')", t)
        print(f"Row {i} [{t}]: isPending={eval_pending}, display='{display}'")
    
    browser.close()
