import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def print_issues():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    # Find and click DELIVERABLE AUTOQC accordion header
    header = page.locator('div.cursor-pointer:has-text("DELIVERABLE AUTOQC")')
    if await header.count() > 0:
        await header.first.scroll_into_view_if_needed()
        await header.first.click()
        await asyncio.sleep(2)

    # Let's extract all the text in the DELIVERABLE AUTOQC section
    card = page.locator('div:has-text("Run AutoQC to check your work")')
    count = await card.count()
    if count > 0:
        text = await card.last.inner_text()
        print('=== AUTOQC SECTION TEXT ===')
        print(text)
        print('===========================')
    else:
        print('Card not found, dumping body:')
        body = await page.evaluate('() => document.body.innerText')
        print(body[:2000])

asyncio.run(print_issues())
