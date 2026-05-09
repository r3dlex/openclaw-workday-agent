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

# Click on Actions button using the correct data-automation-id
ws.send(json.dumps({'id': 1, 'method': 'Runtime.evaluate', 'params': {'expression': '''
(function() {
    const btns = document.querySelectorAll("button");
    for (const btn of btns) {
        if (btn.innerText === "Actions") {
            btn.click();
            return "clicked Actions";
        }
    }
    return "not found";
})()
'''}}))
ws.recv()
time.sleep(2)

ws.send(json.dumps({'id': 2, 'method': 'Runtime.evaluate', 'params': {'expression': 'document.body.innerText.substring(0, 3000)'}}))
resp = json.loads(ws.recv())
text = resp.get('result',{}).get('result',{}).get('value','')
# Look for dropdown menu items
idx = text.find('Add')
if idx < 0: idx = text.find('Enter')
if idx < 0: idx = text.find('Neu')
print(f'After Actions click: ...{text[max(0,idx-100):idx+500]}')
ws.close()