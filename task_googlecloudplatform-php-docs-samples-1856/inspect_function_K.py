import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def inspect_k():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    content = await page.evaluate('''async () => {
        const u = "https://studio.mercor.com/_next/static/immutable/chunks/1e82ttylgxgtq.js";
        const r = await fetch(u);
        const text = await r.text();
        const idx = text.indexOf('autoqc_resolution_required');
        // Let's find function K definition before this snippet
        const before = text.slice(Math.max(0, idx - 2000), idx);
        return before;
    }''')

    print("=== CODE BEFORE autoqc_resolution_required ===")
    print(content)
    print("==============================================")

    await p.stop()

if __name__ == '__main__':
    asyncio.run(inspect_k())
