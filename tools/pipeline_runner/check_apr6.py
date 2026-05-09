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
        
        # Show all days and their hours status
        lines = text.split('\n')
        current_day = ''
        for line in lines:
            line = line.strip()
            if 'Mo.,' in line or 'Di.,' in line or 'Mi.,' in line or 'Do.,' in line or 'Fr.,' in line:
                current_day = line
            elif 'Hours:' in line and current_day:
                print(f'  {current_day}: {line}')
                current_day = ''
        
        # Try clicking Actions then Quick Add to see the dropdown menu
        result = await page.evaluate("""
(function() {
    const btns = document.querySelectorAll("button");
    for (const btn of btns) {
        if (btn.innerText === "Actions") { btn.click(); return "clicked Actions"; }
    }
    return "not found";
})()
""")
        print(f'Actions: {result}')
        await asyncio.sleep(1.5)
        
        # Get all text now visible
        text2 = await page.inner_text('body')
        idx = text2.find('Auto-fill')
        print(f'Menu items: {text2[idx:idx+300]}')
        
        # Now try clicking somewhere else to close menu
        await page.keyboard.press('Escape')
        await asyncio.sleep(0.5)

asyncio.run(main())