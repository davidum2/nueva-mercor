import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def find_combobox():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]
    
    triggers = await page.evaluate("""() => {
        const comboboxes = Array.from(document.querySelectorAll('[role="combobox"], button[data-slot*="select"], button[class*="select"]'));
        return comboboxes.map(c => ({
            tag: c.tagName,
            role: c.getAttribute('role'),
            text: c.innerText.trim(),
            html: c.outerHTML.slice(0, 150)
        }));
    }""")
    print("Found triggers:")
    for t in triggers:
        print(" ", t)
    await p.stop()

if __name__ == '__main__':
    asyncio.run(find_combobox())
