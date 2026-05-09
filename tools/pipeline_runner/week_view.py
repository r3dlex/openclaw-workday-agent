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
        
        # Check for Week view toggle and click it
        result = await page.evaluate("""
(function() {
    const btns = document.querySelectorAll("button");
    const results = [];
    btns.forEach(function(b) {
        if (b.offsetParent !== null) {
            const text = b.innerText?.trim() || "";
            if (text === "Week" || text === "Day" || text === "Month") {
                results.push({text: text, disabled: b.disabled, class: b.className.substring(0, 60), automationId: b.getAttribute("data-automation-id")});
            }
        }
    });
    return JSON.stringify(results);
})()
""")
        print(f'View toggle buttons: {result}')
        
        # Click on Week button (should be the view switcher)
        try:
            week_btn = page.locator('button:has-text("Week")').first
            await week_btn.click(timeout=5000)
            print('Clicked Week button')
            await asyncio.sleep(2)
            
            text2 = await page.inner_text('body')
            idx = text2.find('Today')
            print(f'After Week click: {text2[idx:idx+200]}')
        except Exception as e:
            print(f'Week button error: {e}')

asyncio.run(main())