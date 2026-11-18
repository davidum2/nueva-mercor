import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def check_runs():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]
    
    # Click latest run dropdown
    btn = page.locator('button:has-text("Latest run")')
    if await btn.count() > 0:
        await btn.first.click()
        await asyncio.sleep(1)
        menu_items = await page.evaluate("""() => {
            return Array.from(document.querySelectorAll('[role="menuitem"], [role="option"], [data-radix-collection-item]')).map(el => el.innerText.trim());
        }""")
        print("Run menu items:", menu_items)
        await page.screenshot(path='autoqc_dropdown.png')
    await p.stop()

if __name__ == '__main__':
    asyncio.run(check_runs())
