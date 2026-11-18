import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def click_run():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]
    
    btn = page.locator('button:has-text("Run AutoQC")')
    if await btn.count() > 0:
        await btn.first.click()
        print("Clicked Run AutoQC!", flush=True)
        await asyncio.sleep(4)
        is_running = await page.evaluate("() => document.body.innerText.includes('AutoQC is running')")
        print(f"Is running: {is_running}", flush=True)
        await page.screenshot(path='autoqc_run_started.png')
        print("Saved autoqc_run_started.png", flush=True)

    await p.stop()

if __name__ == '__main__':
    asyncio.run(click_run())
