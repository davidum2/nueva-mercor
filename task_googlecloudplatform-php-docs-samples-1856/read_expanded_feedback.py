import asyncio
import json
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def expand_and_read():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    # Find the REVIEWER FEEDBACK header/button
    rf_button = page.locator('button, div, span').filter(has_text="REVIEWER FEEDBACK").first
    print("Found element, clicking to expand...", flush=True)
    await rf_button.click()
    await asyncio.sleep(2)

    await page.screenshot(path='reviewer_feedback_open.png')
    print("Saved reviewer_feedback_open.png")

    # Read the text of the expanded section
    content = await page.evaluate('''() => {
        const header = Array.from(document.querySelectorAll('*')).find(e => e.innerText && e.innerText.includes('REVIEWER FEEDBACK'));
        if (!header) return 'REVIEWER FEEDBACK not found';
        
        let container = header;
        for (let i = 0; i < 5 && container; i++) {
            if (container.parentElement && (container.parentElement.className.includes('border') || container.parentElement.className.includes('rounded') || container.parentElement.tagName === 'SECTION')) {
                container = container.parentElement;
                break;
            }
            container = container.parentElement;
        }
        return container ? container.innerText : header.parentElement.innerText;
    }''')

    print("\n=== EXPANDED REVIEWER FEEDBACK ===")
    print(content)
    print("==================================")

    await p.stop()

if __name__ == '__main__':
    asyncio.run(expand_and_read())
