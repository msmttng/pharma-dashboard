import asyncio
import os
from playwright.async_api import async_playwright
import json

async def dump_medipal_html():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        url = "https://www.medipal-app.com/App/servlet/InvokerServlet"
        await page.goto(url, wait_until="networkidle", timeout=60000)
        
        medipal_id = os.environ.get("MEDIPAL_ID")
        medipal_pw = os.environ.get("MEDIPAL_PW")
        if not medipal_id:
            print("Error: MEDIPAL_ID not set.")
            return

        await page.fill('input[placeholder="ID"], input[type="text"]', medipal_id)
        await page.fill('input[placeholder="パスワード"], input[type="password"]', medipal_pw)
        await page.click('img[src*="login"], button:has-text("ログイン"), .btnLogin')
        
        await page.wait_for_timeout(8000)
        html = await page.content()
        with open("medipal_debug.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("Saved medipal_debug.html")
        await browser.close()

if __name__ == "__main__":
    with open(".env", "r") as f:
        for line in f:
            if "=" in line:
                k, v = line.strip().split("=", 1)
                os.environ[k] = v
    asyncio.run(dump_medipal_html())
