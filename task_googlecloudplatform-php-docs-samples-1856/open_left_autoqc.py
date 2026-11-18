import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def open_left_autoqc():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]
    
    # In the sidebar (TABS)
    res = await page.evaluate("""() => {
        const sidebar = Array.from(document.querySelectorAll('*')).find(el => el.innerText && el.innerText.includes('TABS'));
        const autoqcItem = Array.from(document.querySelectorAll('*')).find(el => el.innerText && el.innerText.trim() === 'Deliverable AutoQC' && el.children.length === 0);
        if (autoqcItem) {
            autoqcItem.click();
            return { ok: true, text: autoqcItem.innerText };
        }
        return { ok: false };
    }""")
    print("Click result:", res)
    await asyncio.sleep(3)
    await page.screenshot(path='autoqc_sidebar_clicked.png')
    print("Saved autoqc_sidebar_clicked.png")
    
    # Check what is now displayed
    text = await page.evaluate("""() => {
        return document.body.innerText.slice(0, 1000);
    }""")
    print("Body text snippet:\n", text[:600])

    await p.stop()

if __name__ == '__main__':
    asyncio.run(open_left_autoqc())
