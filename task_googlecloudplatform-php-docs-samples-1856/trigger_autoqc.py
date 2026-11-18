import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def trigger_autoqc():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]
    
    # Click the Run AutoQC button
    run_btn = page.locator('button:has-text("Run AutoQC")')
    if await run_btn.count() > 0:
        print("Clicking Run AutoQC button...", flush=True)
        await run_btn.first.click()
        print("Run AutoQC clicked. Waiting 5s...", flush=True)
        await asyncio.sleep(5)
        await page.screenshot(path='autoqc_running.png')
        print("Saved autoqc_running.png", flush=True)
        
    await p.stop()

if __name__ == '__main__':
    asyncio.run(trigger_autoqc())
