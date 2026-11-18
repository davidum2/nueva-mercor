import asyncio
from playwright.async_api import async_playwright

TASK_ID = "task_a6c044440a2b440a9d578ad5c375ad94"

async def click_autoqc():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if 'rubric' not in pg.url and TASK_ID in pg.url and 'sign-in' not in pg.url]
    if task_pages:
        tpage = task_pages[0]
        # Find element by locator
        loc = tpage.locator('text=Deliverable AutoQC')
        count = await loc.count()
        print(f"Locator count: {count}")
        for i in range(count):
            el = loc.nth(i)
            if await el.is_visible():
                print(f"Clicking index {i}...")
                await el.click()
                await asyncio.sleep(2)
                await tpage.screenshot(path='after_clicking_autoqc.png')
                print("Screenshot saved to after_clicking_autoqc.png")
                break
    await p.stop()

if __name__ == '__main__':
    asyncio.run(click_autoqc())
