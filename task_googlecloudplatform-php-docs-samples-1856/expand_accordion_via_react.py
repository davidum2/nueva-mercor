import asyncio
import json
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def expand_react():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    res = await page.evaluate("""() => {
        const div = Array.from(document.querySelectorAll('div')).find(d => {
            return d.className.includes('cursor-pointer') && d.innerText && d.innerText.trim().startsWith('DELIVERABLE AUTOQC');
        });
        if (!div) return { ok: false, error: 'div not found' };

        // Try direct click
        div.click();

        // Also check React Fiber/props onClick
        const fiberKey = Object.keys(div).find(k => k.startsWith('__reactFiber') || k.startsWith('__reactProps'));
        let invokedReact = false;
        if (fiberKey) {
            const prop = div[fiberKey];
            if (prop && prop.onClick) {
                prop.onClick({ preventDefault: () => {}, stopPropagation: () => {} });
                invokedReact = true;
            } else if (prop && prop.memoizedProps && prop.memoizedProps.onClick) {
                prop.memoizedProps.onClick({ preventDefault: () => {}, stopPropagation: () => {} });
                invokedReact = true;
            }
        }

        return { ok: true, invokedReact };
    }""")
    print("Expand result:", res)
    await asyncio.sleep(2)

    # Check what is now inside the DELIVERABLE AUTOQC card
    content = await page.evaluate("""() => {
        const card = Array.from(document.querySelectorAll('div')).find(d => {
            return d.className.includes('border rounded-lg') && d.innerText && d.innerText.includes('DELIVERABLE AUTOQC');
        });
        return card ? card.innerText : 'CARD NOT FOUND';
    }""")

    print("\n--- Card Content ---\n", content[:2000])

    await page.screenshot(path='autoqc_card_expanded.png')
    print("Saved autoqc_card_expanded.png")

    await p.stop()

if __name__ == '__main__':
    asyncio.run(expand_react())
