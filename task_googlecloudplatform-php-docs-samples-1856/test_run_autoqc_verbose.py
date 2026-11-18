import asyncio
import json
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def test_run():
    print("Starting Playwright...", flush=True)
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    print("Connected to CDP.", flush=True)
    pages = browser.contexts[0].pages
    print(f"Total pages: {len(pages)}", flush=True)
    for i, pg in enumerate(pages):
        print(f"  Page {i}: {pg.url}", flush=True)
    
    task_pages = [pg for pg in pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    if not task_pages:
        print("Task page not found!", flush=True)
        await p.stop()
        return

    page = task_pages[0]
    print("Found task page:", page.url, flush=True)

    # Click Deliverable AutoQC tab
    autoqc_tab = page.locator('span:has-text("Deliverable AutoQC")')
    if await autoqc_tab.count() > 0:
        print("Clicking Deliverable AutoQC tab...", flush=True)
        await autoqc_tab.first.click()
        await asyncio.sleep(2)

    # Click Run AutoQC
    run_btn = page.locator('button:has-text("Run AutoQC")')
    cnt = await run_btn.count()
    print(f"Run AutoQC buttons found: {cnt}", flush=True)
    if cnt > 0:
        is_dis = await run_btn.first.is_disabled()
        print(f"Run AutoQC disabled: {is_dis}", flush=True)
        if not is_dis:
            print("Clicking Run AutoQC...", flush=True)
            await run_btn.first.click()
            await asyncio.sleep(3)

    # Check Toast/Modal
    toast = await page.evaluate('''() => {
        const els = Array.from(document.querySelectorAll('[role="status"], [role="alert"], div[class*="toast"], div[class*="modal"]'));
        return els.map(e => e.innerText.trim()).filter(Boolean);
    }''')
    print("Toast/Modal text:", toast, flush=True)

    # Take screenshot
    await page.screenshot(path='autoqc_tab_state.png')
    print("Saved autoqc_tab_state.png", flush=True)

    await p.stop()

if __name__ == '__main__':
    asyncio.run(test_run())
