import asyncio
from playwright.async_api import async_playwright
import json, urllib.request

async def main():
    r = urllib.request.urlopen('http://127.0.0.1:18800/json/version', timeout=3)
    version = json.loads(r.read())
    browser_ws = version['webSocketDebuggerUrl']
    
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(browser_ws)
        ctx = browser.contexts[0]
        
        page = ctx.pages[0]
        
        # Try navigating directly to Workday with existing session
        print('Trying direct Workday URL...')
        await page.goto('https://wd3.myworkday.com/aveva/d/inst/247$15285/rel-task/2998$10955.htmld')
        await asyncio.sleep(5)
        
        print(f'URL: {page.url}')
        text = await page.inner_text('body')
        idx = text.find('Today')
        if idx >= 0:
            print(f'Logged in! Week: {text[idx:text.find("Week",idx)+4]}')
        else:
            print(f'Not logged in. Body: {text[:400]}')

asyncio.run(main())