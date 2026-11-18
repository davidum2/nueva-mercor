import asyncio
import json
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def inspect():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    dom_info = await page.evaluate("""() => {
        // Find all elements containing DELIVERABLE AUTOQC in middle pane
        const els = Array.from(document.querySelectorAll('*')).filter(el => {
            return el.innerText && el.innerText.trim().startsWith('DELIVERABLE AUTOQC') && el.children.length < 5;
        });

        const details = els.map(el => {
            const key = Object.keys(el).find(k => k.startsWith('__reactFiber') || k.startsWith('__reactProps'));
            const props = key ? el[key] : null;
            return {
                tag: el.tagName,
                className: el.className,
                text: el.innerText.trim(),
                hasOnClick: typeof el.onclick === 'function' || !!(props && (props.onClick || props.memoizedProps?.onClick)),
                parentTag: el.parentElement ? el.parentElement.tagName : null,
                parentClass: el.parentElement ? el.parentElement.className : null
            };
        });

        // Also check if there's a chevron icon
        const svgs = Array.from(document.querySelectorAll('svg')).map(s => ({
            parentText: s.parentElement ? s.parentElement.innerText.trim() : '',
            parentTag: s.parentElement ? s.parentElement.tagName : ''
        })).filter(s => s.parentText.includes('AUTOQC'));

        return { details, svgs };
    }""")

    print(json.dumps(dom_info, indent=2))

    await p.stop()

if __name__ == '__main__':
    asyncio.run(inspect())
