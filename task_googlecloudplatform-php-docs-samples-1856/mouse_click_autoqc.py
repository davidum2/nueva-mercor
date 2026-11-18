import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def mouse_click():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]
    
    loc = page.locator('.cursor-pointer:has-text("DELIVERABLE AUTOQC")')
    count = await loc.count()
    print("Found cursor-pointer elements:", count)
    if count > 0:
        box = await loc.first.bounding_box()
        print("Bounding box:", box)
        if box:
            await page.mouse.click(box['x'] + 50, box['y'] + 15)
            print("Clicked with mouse!")
            await asyncio.sleep(2)
            await page.screenshot(path='autoqc_mouse_clicked.png')
            print("Saved autoqc_mouse_clicked.png")
            
            # Print text inside the middle pane
            text = await page.evaluate("""() => {
                const pane = document.querySelector('.py-6');
                return pane ? pane.innerText : '';
            }""")
            print("Middle pane text:\n", text[:800])
            
    await p.stop()

if __name__ == '__main__':
    asyncio.run(mouse_click())
