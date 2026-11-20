import urllib.request, json, websocket, time

tabs = json.loads(urllib.request.urlopen('http://127.0.0.1:9223/json/list').read().decode())
ws_url = [t['webSocketDebuggerUrl'] for t in tabs if '531f225fd0c74bc1a473541ac007fa95' in t.get('url','')][0]
ws = websocket.create_connection(ws_url)

js_rect = """
(() => {
  const b = [...document.querySelectorAll('button')].find(el => el.innerText && el.innerText.includes('Run 12 of 14'));
  if (!b) return null;
  b.scrollIntoView({block: 'center'});
  const r = b.getBoundingClientRect();
  return JSON.stringify({x: r.x + r.width/2, y: r.y + r.height/2, text: b.innerText});
})()
"""
ws.send(json.dumps({'id': 1, 'method': 'Runtime.evaluate', 'params': {'expression': js_rect, 'returnByValue': True}}))
pos = json.loads(json.loads(ws.recv())['result']['result']['value'])
print('POS:', pos)

for ev in ['mousePressed', 'mouseReleased']:
    ws.send(json.dumps({'id': 2, 'method': 'Input.dispatchMouseEvent', 'params': {'type': ev, 'x': pos['x'], 'y': pos['y'], 'button': 'left', 'clickCount': 1}}))
    ws.recv()
time.sleep(0.8)

js_menu = """
(() => {
  const items = [...document.querySelectorAll('[role="menuitem"], [role="option"], [data-radix-collection-item]')];
  return JSON.stringify(items.map(el => {
    const r = el.getBoundingClientRect();
    return {text: el.innerText.trim(), x: r.x + r.width/2, y: r.y + r.height/2};
  }), null, 2);
})()
"""
ws.send(json.dumps({'id': 3, 'method': 'Runtime.evaluate', 'params': {'expression': js_menu, 'returnByValue': True}}))
menu_raw = json.loads(ws.recv())['result']['result']['value']
print('MENU:', menu_raw)
items = json.loads(menu_raw)
if items:
    # click the first item (usually Latest / Run 14)
    target = items[0]
    for ev in ['mousePressed', 'mouseReleased']:
        ws.send(json.dumps({'id': 4, 'method': 'Input.dispatchMouseEvent', 'params': {'type': ev, 'x': target['x'], 'y': target['y'], 'button': 'left', 'clickCount': 1}}))
        ws.recv()
    time.sleep(1.2)
    ws.send(json.dumps({'id': 5, 'method': 'Runtime.evaluate', 'params': {'expression': 'document.body.innerText', 'returnByValue': True}}))
    res = json.loads(ws.recv())['result']['result']['value']
    idx = res.find('COMPACTION RUBRIC QC')
    print('=== LATEST RUBRIC QC ===')
    print(res[idx:] if idx != -1 else res[-4000:])
ws.close()
