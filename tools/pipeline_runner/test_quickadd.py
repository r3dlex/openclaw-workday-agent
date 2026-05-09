import asyncio
import json
import urllib.request
import websocket
import time

r = urllib.request.urlopen('http://127.0.0.1:18800/json/version', timeout=3)
version = json.loads(r.read())

r2 = urllib.request.urlopen('http://127.0.0.1:18800/json', timeout=3)
targets = json.loads(r2.read())
wd = next(t for t in targets if 'inst/247' in t.get('url','') and t['type']=='page')
page_ws = wd['webSocketDebuggerUrl']

ws = websocket.create_connection(page_ws, origin='http://127.0.0.1:18800', timeout=15)
ws.settimeout(10)

# Navigate to Mar 30 - Apr 5 week first
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

# Navigate to Mar 30 - Apr 5 (3 prev clicks from Apr 20-26)
for i in range(3):
    ws.send(json.dumps({'id': i+1, 'method': 'Runtime.evaluate', 'params': {'expression': js_click_prev}}))
    ws.recv()
    time.sleep(1.5)

ws.send(json.dumps({'id': 10, 'method': 'Runtime.evaluate', 'params': {'expression': 'document.body.innerText.substring(document.body.innerText.indexOf("Today"), document.body.innerText.indexOf("Today")+50)'}}))
resp = json.loads(ws.recv())
print(f'Week: {resp.get("result",{}).get("result",{}).get("value","")}')

# Click Actions
ws.send(json.dumps({'id': 11, 'method': 'Runtime.evaluate', 'params': {'expression': '''
(function() {
    const btns = document.querySelectorAll("button");
    for (const btn of btns) {
        if (btn.innerText === "Actions") { btn.click(); return "clicked Actions"; }
    }
    return "not found";
})()
'''}}))
ws.recv()
time.sleep(1.5)

# Click Quick Add
ws.send(json.dumps({'id': 12, 'method': 'Runtime.evaluate', 'params': {'expression': '''
(function() {
    const btns = document.querySelectorAll("button");
    for (const btn of btns) {
        if (btn.innerText === "Quick Add") { btn.click(); return "clicked Quick Add"; }
    }
    return "not found";
})()
'''}}))
ws.recv()
time.sleep(2)

# Check what appeared
ws.send(json.dumps({'id': 13, 'method': 'Runtime.evaluate', 'params': {'expression': 'document.body.innerText.substring(0, 4000)'}}))
resp = json.loads(ws.recv())
text = resp.get('result',{}).get('result',{}).get('value','')
print(f'After Quick Add ({len(text)} chars):')
# Look for dialog/modal
idx = text.find('Block')
if idx < 0: idx = text.find('Start')
if idx < 0: idx = text.find('Hours')
print(text[max(0,idx-200):idx+800])
ws.close()