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
        
        # Click on Fr 10.4 cell (should be empty since Hours: 0)
        result = await page.evaluate("""
(function() {
    const all = document.querySelectorAll("*");
    for (const e of all) {
        if (e.childNodes.length === 1 && e.innerText === "Fr., 10.4.") {
            e.click();
            return "clicked Fr 10.4";
        }
    }
    return "not found";
})()
""")
        print(f'Click Fr 10.4: {result}')
        await asyncio.sleep(1.5)
        
        # Click Actions
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
        await asyncio.sleep(1)
        
        # Click Quick Add
        result = await page.evaluate("""
(function() {
    const btns = document.querySelectorAll("button");
    for (const btn of btns) {
        if (btn.innerText === "Quick Add") { btn.click(); return "clicked Quick Add"; }
    }
    return "not found";
})()
""")
        print(f'Quick Add: {result}')
        await asyncio.sleep(3)
        
        # Get the entire body text
        text2 = await page.inner_text('body')
        print(f'Full body (3000 chars):')
        print(text2[:3000])
        
        # Also get HTML of any dialog/popup
        result = await page.evaluate("""
(function() {
    const popups = document.querySelectorAll("[data-automation-widget='wd-popup']");
    const results = [];
    popups.forEach(function(p) {
        if (p.offsetParent !== null) {
            results.push({tag: p.tagName, class: p.className, html: p.outerHTML.substring(0, 800)});
        }
    });
    return JSON.stringify(results);
})()
""")
        print(f'Popups: {result}')

asyncio.run(main())