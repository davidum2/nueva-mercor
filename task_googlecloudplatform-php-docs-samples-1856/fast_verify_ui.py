import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True)

TASK_ID = "task_a6c044440a2b440a9d578ad5c375ad94"

async def verify():
    print("Connecting to browser...", flush=True)
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    
    # 1. Rubric page
    rubric_pages = [pg for pg in browser.contexts[0].pages if 'rubric' in pg.url and TASK_ID in pg.url]
    if rubric_pages:
        rpage = rubric_pages[0]
        print(f"Found rubric page: {rpage.url}", flush=True)
        await rpage.reload(wait_until='domcontentloaded')
        await asyncio.sleep(3)
        await rpage.screenshot(path='rubric_page_injected.png')
        print("Captured rubric_page_injected.png", flush=True)

    # 2. Main task page
    task_pages = [pg for pg in browser.contexts[0].pages if 'rubric' not in pg.url and TASK_ID in pg.url and 'sign-in' not in pg.url]
    if task_pages:
        tpage = task_pages[0]
        print(f"Found task page: {tpage.url}", flush=True)
        await tpage.reload(wait_until='domcontentloaded')
        await asyncio.sleep(3)
        await tpage.screenshot(path='task_page_injected.png')
        print("Captured task_page_injected.png", flush=True)
        
        # Check text in AutoQC if present
        autoqc_btn = await tpage.query_selector('button:has-text("AutoQC"), [role="tab"]:has-text("AutoQC"), div:has-text("AutoQC")')
        print(f"AutoQC element found: {autoqc_btn is not None}", flush=True)

    await p.stop()
    print("Verification completed successfully!", flush=True)

if __name__ == '__main__':
    asyncio.run(verify())
