import asyncio
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_f5ba2eb1464a4db2831f60a63283341d'

async def capture_network():
    p = await async_playwright().start()
    b = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [pg for pg in b.contexts[0].pages if TASK_ID in pg.url and 'rubric' not in pg.url][0]

    captured = []
    page.on('request', lambda req: captured.append({'method': req.method, 'url': req.url}) if any(k in req.url for k in ['transcript', 'files', 's3', 'artifact', 'rollout']) else None)

    # Click Model A then Model B
    print("Clicking Model A...")
    await page.evaluate('''() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const m = btns.find(b => (b.innerText || '').trim() === 'Model A');
        if (m) m.click();
    }''')
    await asyncio.sleep(2)

    print("Clicking Model B...")
    await page.evaluate('''() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const m = btns.find(b => (b.innerText || '').trim() === 'Model B');
        if (m) m.click();
    }''')
    await asyncio.sleep(2)

    print(f"Captured {len(captured)} matching requests:")
    for c in captured:
        print(" ->", c['method'], c['url'][:120])

    await p.stop()

if __name__ == '__main__':
    asyncio.run(capture_network())
