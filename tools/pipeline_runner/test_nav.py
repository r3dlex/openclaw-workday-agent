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
        
        # Navigate to Mar 30 - Apr 5 (3 prev from Apr 20-26)
        for i in range(3):
            result = await page.evaluate(js_click_prev)
            print(f'Click {i+1}: {result}')
            await asyncio.sleep(2)  # Wait longer between clicks
        
        text = await page.inner_text('body')
        idx = text.find('Today')
        end = text.find('Week', idx)
        current = text[idx:end+4]
        print(f'Week: {current}')
        
        # Show all days
        for day in ['Mo.', 'Di.', 'Mi.', 'Do.', 'Fr.']:
            idx = text.find(day)
            if idx >= 0:
                end = text.find('\n', idx)
                print(f'  {text[idx:end]}')

asyncio.run(main())