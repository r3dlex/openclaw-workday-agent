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
        
        # Try navigating directly to Enter Time via the sidebar link
        # Check URL structure
        result = await page.evaluate("""
(function() {
    // Find the Enter Time link
    const links = document.querySelectorAll("a");
    const results = [];
    links.forEach(function(l) {
        if (l.offsetParent !== null && (l.innerText.includes("Enter") || l.href.includes("inst/247"))) {
            results.push({text: l.innerText?.trim(), href: l.href});
        }
    });
    return JSON.stringify(results);
})()
""")
        print(f'Links: {result}')
        
        # Try clicking on Enter My Time in sidebar
        try:
            enter_link = page.locator('text="Enter My Time"').first
            await enter_link.click(timeout=5000)
            print('Clicked Enter My Time')
            await asyncio.sleep(3)
            
            text2 = await page.inner_text('body')
            idx = text2.find('Today')
            print(f'After Enter My Time: {text2[idx:idx+200]}')
        except Exception as e:
            print(f'Enter My Time error: {e}')

asyncio.run(main())