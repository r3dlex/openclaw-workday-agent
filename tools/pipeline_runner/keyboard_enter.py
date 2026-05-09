import asyncio
from playwright.async_api import async_playwright
import json, urllib.request

js_click_prev = """
(function() {
    var btn = document.querySelector("[aria-label='Previous Week']");
    if (!btn) return 'not found';
    btn.scrollIntoView({block: 'center'});
    var rect = btn.getBoundingClientRect();
    var cx = rect.left + rect.width/2;
    var cy = rect.top + rect.height/2;
    var opts = {bubbles: true, cancelable: true, view: window, clientX: cx, clientY: cy};
    btn.dispatchEvent(new MouseEvent('mouseenter', opts));
    btn.dispatchEvent(new MouseEvent('mouseover', opts));
    btn.dispatchEvent(new MouseEvent('mousemove', opts));
    btn.dispatchEvent(new MouseEvent('mousedown', opts));
    btn.dispatchEvent(new MouseEvent('mouseup', opts));
    btn.dispatchEvent(new MouseEvent('click', opts));
    return 'clicked';
})()
"""

async def main():
    r = urllib.request.urlopen('http://127.0.0.1:18800/json/version', timeout=3)
    version = json.loads(r.read())
    browser_ws = version['webSocketDebuggerUrl']
    
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(browser_ws)
        ctx = browser.contexts[0]
        
        page = ctx.pages[0]
        await page.goto('https://wd3.myworkday.com/aveva/d/inst/247$15285/rel-task/2998$10955.htmld')
        await asyncio.sleep(4)
        
        # Go back 2 weeks to Apr 6-12
        for i in range(2):
            await page.evaluate(js_click_prev)
            await asyncio.sleep(2)
        
        text = await page.inner_text('body')
        idx = text.find('Today')
        end = text.find('Week', idx)
        print(f'Week: {text[idx:end+4]}')
        
        # Focus on the Fr 10.4 cell and press Enter/Space
        try:
            fr_cell = page.locator('[data-automation-id="dayCell-3-10"]')
            await fr_cell.focus()
            print('Focused Fr 10.4 cell')
            await asyncio.sleep(0.5)
            
            # Press Enter
            await page.keyboard.press('Enter')
            print('Pressed Enter')
            await asyncio.sleep(2)
            
            text2 = await page.inner_text('body')
            if 'Hours Worked' in text2:
                idx = text2.find('Hours Worked')
                print(f'Entry form: {text2[idx:idx+800]}')
            else:
                print('No entry form')
                
            # Try Space
            await page.keyboard.press('Space')
            print('Pressed Space')
            await asyncio.sleep(2)
            
            text3 = await page.inner_text('body')
            if 'Hours Worked' in text3:
                idx = text3.find('Hours Worked')
                print(f'Entry form after Space: {text3[idx:idx+500]}')
            else:
                print('No entry form after Space')
        except Exception as e:
            print(f'Error: {e}')
        
        # Also try Review button
        try:
            review_btn = page.locator('button:has-text("Review")')
            await review_btn.click(timeout=5000)
            print('Clicked Review')
            await asyncio.sleep(2)
            
            text4 = await page.inner_text('body')
            idx = text4.find('Today')
            print(f'After Review: {text4[idx:idx+200]}')
        except Exception as e:
            print(f'Review error: {e}')

asyncio.run(main())