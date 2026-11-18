import asyncio
import json
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def switch():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    # Find the sidebar navigation items
    res = await page.evaluate("""() => {
        const buttons = Array.from(document.querySelectorAll('button')).filter(b => {
            return b.innerText && (b.innerText.trim() === 'Deliverable AutoQC' || b.getAttribute('title') === 'Deliverable AutoQC');
        });
        
        if (buttons.length > 0) {
            // Click the button using dispatchEvent and click
            buttons[0].dispatchEvent(new MouseEvent('mousedown', { bubbles: true }));
            buttons[0].dispatchEvent(new MouseEvent('mouseup', { bubbles: true }));
            buttons[0].click();
            return { clicked: true, className: buttons[0].className, text: buttons[0].innerText };
        }
        return { clicked: false };
    }""")
    print("Switch result:", res)
    await asyncio.sleep(2)

    await page.screenshot(path='after_proper_switch.png')
    print("Saved after_proper_switch.png")

    await p.stop()

if __name__ == '__main__':
    asyncio.run(switch())
