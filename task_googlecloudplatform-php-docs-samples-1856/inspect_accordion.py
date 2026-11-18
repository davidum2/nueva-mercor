import asyncio
import json
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def inspect_accordion():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    # Find the accordion header for DELIVERABLE AUTOQC
    res = await page.evaluate("""() => {
        const els = Array.from(document.querySelectorAll('*')).filter(el => {
            return el.innerText && el.innerText.trim().startsWith('DELIVERABLE AUTOQC') && el.children.length <= 2;
        });
        
        // Find the clickable trigger
        const triggers = els.map(el => ({
            tag: el.tagName,
            className: el.className,
            text: el.innerText.trim(),
            ariaExpanded: el.getAttribute('aria-expanded'),
            role: el.getAttribute('role')
        }));

        // Try to click the trigger
        let clicked = false;
        for (const el of els) {
            el.click();
            clicked = true;
            break;
        }

        return { triggers, clicked };
    }""")
    print("Accordion click result:", json.dumps(res, indent=2))
    await asyncio.sleep(2)

    await page.screenshot(path='after_accordion_click.png')
    print("Saved after_accordion_click.png")

    await p.stop()

if __name__ == '__main__':
    asyncio.run(inspect_accordion())
