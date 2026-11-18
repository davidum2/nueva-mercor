import asyncio
import json
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def test_tab():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    btn = page.locator('button[title="Deliverable AutoQC"]')
    count = await btn.count()
    print("Found Deliverable AutoQC buttons:", count)
    if count > 0:
        await btn.first.click(force=True)
        print("Clicked with force=True!")
        await asyncio.sleep(2)

    await page.screenshot(path='after_force_click_tab.png')
    print("Saved after_force_click_tab.png")

    await p.stop()

if __name__ == '__main__':
    asyncio.run(test_tab())
