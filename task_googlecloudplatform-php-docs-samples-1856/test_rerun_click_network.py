import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def test_rerun():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    # Track all requests
    page.on('request', lambda r: print(f"REQ -> {r.method} {r.url}") if 'api' in r.url or 'mercor' in r.url else None)
    page.on('response', lambda r: print(f"RES <- {r.status} {r.url}") if 'api' in r.url or 'mercor' in r.url else None)

    # 1. Click 'Add to rerun'
    add_btn = page.locator('button:text-is("Add to rerun")')
    count = await add_btn.count()
    print("Found 'Add to rerun' count:", count)
    if count > 0:
        await add_btn.first.click()
        print("Clicked 'Add to rerun'!")
        await asyncio.sleep(2)

    # Check state of 'Rerun X selected' button
    sel_btn = page.locator('button:has-text("Rerun")').filter(has_text="selected")
    count_sel = await sel_btn.count()
    if count_sel > 0:
        text = await sel_btn.first.inner_text()
        disabled = await sel_btn.first.is_disabled()
        print(f"Selected button: '{text}', disabled={disabled}")
        if not disabled:
            print("Clicking selected rerun button...")
            await sel_btn.first.click()
            await asyncio.sleep(5)

    # If selected button wasn't clicked or failed, try 'Rerun 1 failing'
    failing_btn = page.locator('button:text-is("Rerun 1 failing")')
    if await failing_btn.count() > 0 and count_sel == 0:
        print("Clicking 'Rerun 1 failing'...")
        await failing_btn.first.click()
        await asyncio.sleep(5)

    await page.screenshot(path='after_test_rerun.png')
    print("Saved after_test_rerun.png")

    await p.stop()

if __name__ == '__main__':
    asyncio.run(test_rerun())
