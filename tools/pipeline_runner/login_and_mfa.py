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
        
        # Navigate to login
        print('Navigating to login...')
        await page.goto('https://wd3-identity.myworkday.com/wday/authgwy/aveva/upc/login')
        await asyncio.sleep(3)
        
        print(f'URL: {page.url}')
        text = await page.inner_text('body')
        
        if 'sign in' in text.lower()[:200]:
            print('On login page, clicking RIB...')
            try:
                rib = page.locator('text=RIB').first
                await rib.click(timeout=8000)
                print('Clicked RIB')
                await asyncio.sleep(6)
                print(f'URL after RIB: {page.url}')
            except Exception as e:
                print(f'RIB click error: {e}')
            
            text = await page.inner_text('body')
        
        if 'microsoft' in page.url.lower() or 'deviceauth' in page.url.lower():
            print('On Microsoft login page')
            try:
                email_input = page.locator('[type="email"], [name="email"], input[type="text"]').first
                await email_input.fill('andre.burgstahler@rib-software.com')
                await page.keyboard.press('Enter')
                await asyncio.sleep(4)
                print(f'Email entered, URL: {page.url}')
            except Exception as e:
                print(f'Email error: {e}')
            
            text = await page.inner_text('body')
            if 'code' in text.lower() or 'verification' in text.lower() or 'approve' in text.lower():
                print('MFA prompt shown - need manual code')
            else:
                idx = text.find('Today')
                if idx >= 0:
                    print(f'Week: {text[idx:text.find("Week",idx)+4]}')
                else:
                    print(f'Body: {text[:500]}')
        elif 'login' not in page.url.lower() and 'today' in text.lower():
            idx = text.find('Today')
            print(f'Week: {text[idx:text.find("Week",idx)+4]}')
        else:
            print(f'Not logged in yet, body: {text[:300]}')

asyncio.run(main())