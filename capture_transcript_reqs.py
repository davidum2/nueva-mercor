import asyncio
import json
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_08ccf272669347c3af63de71b2ecb5e5'

async def capture_network():
    p = await async_playwright().start()
    b = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [pg for pg in b.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url][0]

    captured_urls = []
    def on_req(req):
        if any(k in req.url for k in ['transcript', 's3', 'files', 'presigned', 'sign']):
            captured_urls.append((req.method, req.url))

    page.on('request', on_req)

    # Click Trajectory Viewer tab
    print("Clicking Trajectory Viewer in sidebar...")
    await page.evaluate('''() => {
        const btns = Array.from(document.querySelectorAll('button, div, span'));
        const tab = btns.find(b => b.innerText && b.innerText.trim() === 'Trajectory Viewer');
        if (tab) tab.click();
    }''')
    await asyncio.sleep(2)

    # Click 1 · Agent solution A
    await page.evaluate('''() => {
        const btns = Array.from(document.querySelectorAll('button, div, span'));
        const tab = btns.find(b => b.innerText && b.innerText.trim() === '1 · Agent solution A');
        if (tab) tab.click();
    }''')
    await asyncio.sleep(2)

    # Click 1 · Agent solution B
    await page.evaluate('''() => {
        const btns = Array.from(document.querySelectorAll('button, div, span'));
        const tab = btns.find(b => b.innerText && b.innerText.trim() === '1 · Agent solution B');
        if (tab) tab.click();
    }''')
    await asyncio.sleep(2)

    print("Captured relevant requests:")
    for method, u in captured_urls:
        print(f"  {method} {u}")

    await b.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(capture_network())
