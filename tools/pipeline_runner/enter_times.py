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

async def get_day_cell(page, day_text):
    """Find a day cell by its text like 'Mi., 1.4.'"""
    result = await page.evaluate("""
function findDayCell(text) {
    const all = document.querySelectorAll("*");
    for (const e of all) {
        if (e.childNodes.length === 1 && e.innerText === text) {
            return e.outerHTML;
        }
    }
    return null;
}
findDayCell(arguments[0])
""", day_text)
    return result

async def click_actions_and_quick_add(page):
    """Click Actions then Quick Add"""
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
    await asyncio.sleep(2)
    return result

async def main():
    r = urllib.request.urlopen('http://127.0.0.1:18800/json/version', timeout=3)
    version = json.loads(r.read())
    browser_ws = version['webSocketDebuggerUrl']
    
    # Times to enter for each day: (start1, end1, start2, end2)
    # Using German format (24h)
    times_to_enter = {
        # Week Mar 30 - Apr 5
        'Mi., 1.4.': ('08:00', '12:30', '13:15', '18:00'),  # 4.5h + 4.75h = 9.25h
        'Do., 2.4.': ('08:00', '12:30', '13:15', '18:30'),  # 4.5h + 5.25h = 9.75h
        # Week Apr 6-12
        'Mo., 6.4.': ('08:00', '12:30', '13:15', '17:45'),  # 4.5h + 4.5h = 9.0h
        'Di., 7.4.': ('08:00', '12:30', '13:15', '17:45'),  # 4.5h + 4.5h = 9.0h
        'Mi., 8.4.': ('08:00', '12:30', '13:15', '18:15'),  # 4.5h + 4.75h = 9.25h
        'Do., 9.4.': ('08:00', '12:30', '13:15', '18:30'),  # 4.5h + 5.25h = 9.75h
        'Fr., 10.4.': ('08:00', '12:30', '13:15', '18:00'), # 4.5h + 4.75h = 9.25h
        # Week Apr 13-19
        'Mo., 13.4.': ('08:00', '12:30', '13:15', '18:45'), # 4.5h + 5.25h = 9.75h
        'Di., 14.4.': ('08:00', '12:30', '13:15', '18:00'), # 4.5h + 4.75h = 9.25h
        'Mi., 15.4.': ('08:00', '12:30', '13:15', '18:30'), # 4.5h + 5.25h = 9.75h
        # Week Apr 20-26
        'Mo., 20.4.': ('08:00', '12:30', '13:15', '17:45'), # 4.5h + 4.5h = 9.0h
        'Di., 21.4.': ('08:00', '12:30', '13:15', '18:15'), # 4.5h + 4.75h = 9.25h
        'Mi., 22.4.': ('08:00', '12:30', '13:15', '18:45'), # 4.5h + 5.25h = 9.75h
    }
    
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(browser_ws)
        ctx = browser.contexts[0]
        
        page = ctx.pages[0]
        await page.goto('https://wd3.myworkday.com/aveva/d/inst/247$15285/rel-task/2998$10955.htmld')
        await asyncio.sleep(4)
        
        # --- WEEK 1: Mar 30 - Apr 5 (Mi 1, Do 2) ---
        print('=== Navigating to Mar 30 - Apr 5 ===')
        for i in range(3):
            await page.evaluate(js_click_prev)
            await asyncio.sleep(2)
        
        text = await page.inner_text('body')
        idx = text.find('Today')
        print(f'Week: {text[idx:text.find("Week", idx)+4]}')
        
        for day in ['Mi., 1.4.', 'Do., 2.4.']:
            if day in times_to_enter:
                print(f'  Processing {day}...')
                # Click on the day cell
                result = await page.evaluate("""
(function() {
    const all = document.querySelectorAll("*");
    for (const e of all) {
        if (e.childNodes.length === 1 && e.innerText === arguments[0]) {
            e.click();
            return "clicked";
        }
    }
    return "not found";
})()
""", day)
                print(f'    Clicked {day}: {result}')
                await asyncio.sleep(1)
                
                # Use Quick Add
                await click_actions_and_quick_add(page)
                
                # Enter times
                s1, e1, s2, e2 = times_to_enter[day]
                print(f'    Entering {s1}-{e1} and {s2}-{e2}')
                # TODO: Fill in the Quick Add form
                await asyncio.sleep(2)
        
        print('=== Week 1 done ===')

asyncio.run(main())