import asyncio
import json
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def inspect_ui():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    # Reload page with commit to refresh React state cleanly from the backend database!
    print("Reloading page with domcontentloaded to ensure UI loads fresh data from DB...", flush=True)
    await page.goto(page.url, wait_until='domcontentloaded')
    await asyncio.sleep(4)

    # Inspect the verifiers in UI table
    rows = await page.evaluate("""() => {
        // Collect text from rubric table
        const cells = Array.from(document.querySelectorAll('div[role="row"], tr')).map(r => r.innerText);
        return cells.slice(0, 15);
    }""")

    print("UI Table Rows after fresh load:", json.dumps(rows, indent=2))

    await page.screenshot(path='ui_after_db_reload.png')
    print("Saved ui_after_db_reload.png")

    await p.stop()

if __name__ == '__main__':
    asyncio.run(inspect_ui())
