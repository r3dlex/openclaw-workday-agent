import asyncio
from playwright.async_api import async_playwright
import json, urllib.request

js_click = """
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

js_find_buttons = '''
(function() {
    const elements = document.querySelectorAll("button, a, [role=button], input[type=submit], input[type=button]");
    const results = [];
    elements.forEach(function(e) {
        if (e.offsetParent !== null) {
            const text = e.innerText || e.value || "";
            const type = e.type || "";
            const className = e.className || "";
            const automationId = e.getAttribute("data-automation-id") || "";
            if (text.trim() || type) {
                results.push({tag: e.tagName, text: text.trim(), type: type, class: className.substring(0,50), aid: automationId});
            }
        }
    });
    return JSON.stringify(results);
})()
'''

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
        
        # Navigate to Mar 30 - Apr 5
        for i in range(3):
            await page.evaluate(js_click)
            await asyncio.sleep(1.5)
        
        # Double-click Mi 1.4 to open entry form
        mi_cell = page.locator('text="Mi., 1.4."').first
        await mi_cell.dblclick(timeout=5000)
        await asyncio.sleep(2)
        
        result = await page.evaluate(js_find_buttons)
        print(f'Buttons/links: {result}')

asyncio.run(main())