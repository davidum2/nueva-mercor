import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def open_card():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    # Click DELIVERABLE AUTOQC header
    header = page.locator('div.cursor-pointer:has-text("DELIVERABLE AUTOQC")')
    if await header.count() > 0:
        await header.first.scroll_into_view_if_needed()
        await header.first.click()
        await asyncio.sleep(2)

    await page.screenshot(path='autoqc_card_opened.png')
    print("Saved autoqc_card_opened.png")

    text = await page.evaluate('''() => {
        const el = Array.from(document.querySelectorAll('div')).find(d => d.innerText && d.innerText.includes('Run AutoQC to check your work'));
        return el ? el.innerText : 'Not found';
    }''')
    print("Card text:", text)

    await p.stop()

if __name__ == '__main__':
    asyncio.run(open_card())
