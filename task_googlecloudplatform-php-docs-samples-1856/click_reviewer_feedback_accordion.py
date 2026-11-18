import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def click_rf():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    # Find the REVIEWER FEEDBACK element in the middle panel
    res = await page.evaluate('''() => {
        const els = Array.from(document.querySelectorAll('*')).filter(e => {
            const t = e.innerText || '';
            return t === 'REVIEWER FEEDBACK' || (t.includes('REVIEWER FEEDBACK') && t.length < 50);
        });

        const details = els.map(e => ({
            tag: e.tagName,
            className: e.className,
            parentTag: e.parentElement?.tagName,
            parentClass: e.parentElement?.className,
            cursor: window.getComputedStyle(e).cursor
        }));

        // Find the clickable button or div
        for (const el of els) {
            let target = el;
            while (target && target.tagName !== 'BUTTON' && !target.className.includes('cursor-pointer')) {
                target = target.parentElement;
            }
            if (target) {
                target.click();
                return { clicked: true, targetTag: target.tagName, targetClass: target.className };
            }
        }

        return { clicked: false, details };
    }''')

    print("Click result:", res)
    await asyncio.sleep(2)
    await page.screenshot(path='after_rf_click.png')
    print("Saved after_rf_click.png")

    # Read text
    body = await page.evaluate('''() => {
        const container = Array.from(document.querySelectorAll('div')).find(d => d.innerText && d.innerText.includes('Feedback for writer') || d.innerText.includes('Adjudication rationale'));
        return container ? container.innerText : 'Container not found';
    }''')
    print("Text in RF:", body)

    await p.stop()

if __name__ == '__main__':
    asyncio.run(click_rf())
