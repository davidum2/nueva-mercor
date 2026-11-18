import asyncio
import sys
import json
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def trigger_run():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    # Reload page
    print("Reloading page to refresh React state...", flush=True)
    await page.reload(wait_until='domcontentloaded')
    await asyncio.sleep(5)

    # Listen to console and network
    page.on('console', lambda msg: print(f"CONSOLE [{msg.type}]: {msg.text}"))
    page.on('request', lambda req: print(f"REQ: {req.method} {req.url}") if 'autoqc' in req.url or 'run' in req.url or 'verifier' in req.url or 'task' in req.url else None)
    page.on('response', lambda res: print(f"RES: {res.status} {res.url}") if 'autoqc' in res.url or 'run' in res.url or 'verifier' in res.url or 'task' in res.url else None)

    # Expand DELIVERABLE AUTOQC accordion
    header = page.locator('div.cursor-pointer:has-text("DELIVERABLE AUTOQC")')
    count = await header.count()
    print("Header count:", count)
    if count > 0:
        await header.first.scroll_into_view_if_needed()
        await header.first.click()
        await asyncio.sleep(2)

    # Inspect the Run AutoQC button
    run_btn = page.locator('button:has-text("Run AutoQC")')
    btn_count = await run_btn.count()
    print("Run button count:", btn_count)
    if btn_count > 0:
        is_disabled = await run_btn.first.is_disabled()
        is_visible = await run_btn.first.is_visible()
        print(f"Run AutoQC button visible={is_visible}, disabled={is_disabled}")
        await run_btn.first.click()
        print("Clicked Run AutoQC button!", flush=True)
        await asyncio.sleep(4)

    await page.screenshot(path='after_run_click.png')
    print("Saved after_run_click.png")

asyncio.run(trigger_run())
