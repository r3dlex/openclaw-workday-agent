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
        
        # Try to find all visible clickable elements in the day row
        result = await page.evaluate("""
(function() {
    // Get the Fr 10.4 day cell and its container
    const cell = document.querySelector("[data-automation-id='dayCell-3-10']");
    if (!cell) return "cell not found";
    
    // Get the day cell container (should have the hours display)
    const container = cell.parentElement;
    
    // Look for all elements within the day row that are clickable
    // Find the row by going up to TR
    let row = container;
    while (row && row.tagName !== "TR") row = row.parentElement;
    
    // Get all clickable children in the row
    const clickables = [];
    if (row) {
        const all = row.querySelectorAll("*");
        all.forEach(function(e) {
            if (e.offsetParent !== null && (e.onclick || e.getAttribute("role") === "button" || e.tagName === "BUTTON" || e.tagName === "A")) {
                clickables.push({
                    tag: e.tagName,
                    text: e.innerText?.trim().substring(0, 30) || "",
                    automationId: e.getAttribute("data-automation-id") || "",
                    class: e.className?.substring(0, 50) || ""
                });
            }
        });
    }
    
    return JSON.stringify({
        cellHTML: cell.outerHTML,
        containerClass: container?.className,
        rowHTML: row?.innerHTML?.substring(0, 500) || "no row",
        clickables: clickables
    });
})()
""")
        print(f'Day cell info: {result}')

asyncio.run(main())