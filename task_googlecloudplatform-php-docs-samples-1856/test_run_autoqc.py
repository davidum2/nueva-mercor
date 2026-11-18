import asyncio
import json
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def test_run():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    # Navigate to Deliverable AutoQC tab
    autoqc_tab = page.locator('span:has-text("Deliverable AutoQC")')
    if await autoqc_tab.count() > 0:
        await autoqc_tab.first.click()
        await asyncio.sleep(2)

    # Click Run AutoQC
    run_btn = page.locator('button:has-text("Run AutoQC")')
    if await run_btn.count() > 0:
        print("Found Run AutoQC button, clicking...", flush=True)
        await run_btn.first.click()
        await asyncio.sleep(3)

        # Check if modal or toast appeared
        toast = await page.evaluate('''() => {
            const els = Array.from(document.querySelectorAll('[role="status"], [role="alert"], div[class*="toast"], div[class*="modal"]'));
            return els.map(e => e.innerText.trim()).filter(Boolean);
        }''')
        print("Toast/Modal text:", toast, flush=True)

        # Check what the button looks like now
        btn_text = await page.evaluate('''() => {
            const btns = Array.from(document.querySelectorAll('button')).map(b => b.innerText.trim());
            return btns.filter(t => t.includes('AutoQC') || t.includes('run'));
        }''')
        print("Buttons now:", btn_text, flush=True)

    await p.stop()

if __name__ == '__main__':
    asyncio.run(test_run())
