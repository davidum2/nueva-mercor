import asyncio
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_f5ba2eb1464a4db2831f60a63283341d'

async def click_autoqc_tab():
    p = await async_playwright().start()
    b = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [pg for pg in b.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url][0]

    btn = page.locator('button:has-text("Deliverable AutoQC")')
    count = await btn.count()
    print("Found Deliverable AutoQC buttons:", count)
    if count > 0:
        await btn.first.click(force=True)
        print("Clicked Deliverable AutoQC tab!")
        await asyncio.sleep(2)

    await page.screenshot(path='after_autoqc_tab_click.png')
    print("Saved after_autoqc_tab_click.png")

    # Check for Run AutoQC or run button
    run_btn = page.locator('button:has-text("Run AutoQC")')
    print("Run AutoQC count:", await run_btn.count())

    latest_run = page.locator('button:has-text("Latest run")')
    print("Latest run count:", await latest_run.count())

    all_btns = await page.evaluate('''() => {
        return Array.from(document.querySelectorAll('button')).map(b => b.innerText ? b.innerText.trim() : '').filter(t => t.length > 0 && t.length < 50);
    }''')
    print("All buttons on screen:", all_btns)

    await b.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(click_autoqc_tab())
