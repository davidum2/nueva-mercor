import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def click_chevron():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]
    
    # Click the SVG or cursor-pointer div of DELIVERABLE AUTOQC
    div = page.locator('div.cursor-pointer:has-text("DELIVERABLE AUTOQC")')
    count = await div.count()
    print("Found div count:", count)
    if count > 0:
        await div.first.click()
        await asyncio.sleep(2)
        await page.screenshot(path='autoqc_chevron_clicked.png')
        print("Saved autoqc_chevron_clicked.png")
        
        # Check text inside
        txt = await page.evaluate("""() => {
            const el = Array.from(document.querySelectorAll('*')).find(e => e.innerText && e.innerText.includes('Run AutoQC'));
            return el ? el.outerHTML : 'No Run AutoQC button';
        }""")
        print("Run AutoQC check:", txt)

    await p.stop()

if __name__ == '__main__':
    asyncio.run(click_chevron())
