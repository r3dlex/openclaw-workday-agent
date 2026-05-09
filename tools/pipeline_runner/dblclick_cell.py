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
        
        # Try using Playwright's locator with data-automation-id to double-click
        try:
            # Use first() since there might be multiple matching elements
            fr_cell = page.locator('[data-automation-id="dayCell-3-10"]').first
            cell_text = await fr_cell.inner_text()
            print(f'Found cell: {cell_text}')
            
            # Double click using mouse
            await fr_cell.dblclick(timeout=5000)
            print('Double-clicked via Playwright')
            await asyncio.sleep(2)
            
            # Check if anything changed
            text2 = await page.inner_text('body')
            if 'Hours Worked' in text2:
                idx = text2.find('Hours Worked')
                print(f'Entry form: {text2[idx:idx+800]}')
            else:
                print('No entry form appeared')
                # Show what's on the page now
                idx = text2.find('Today')
                print(f'Current: {text2[idx:idx+200]}')
        except Exception as e:
            print(f'Error: {e}')

asyncio.run(main())