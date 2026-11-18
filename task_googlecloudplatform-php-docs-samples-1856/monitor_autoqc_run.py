import asyncio
import json
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def monitor():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    for i in range(15):
        await asyncio.sleep(2)
        info = await page.evaluate('''() => {
            const btns = Array.from(document.querySelectorAll('button')).map(b => b.innerText.trim());
            return btns.filter(t => t.includes('AutoQC') || t.includes('Cancel') || t.includes('run'));
        }''')
        print(f"[{i*2}s] btns: {info}", flush=True)
        if not any('AutoQC is running' in b for b in info):
            print("AutoQC finished or stopped running!", flush=True)
            break

    await page.screenshot(path='autoqc_after_run.png')
    print("Saved autoqc_after_run.png", flush=True)
    await p.stop()

if __name__ == '__main__':
    asyncio.run(monitor())
