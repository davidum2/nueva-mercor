import asyncio
import json
from playwright.async_api import async_playwright

TASK_ID = 'task_08ccf272669347c3af63de71b2ecb5e5'

async def inspect_autoqc_dom():
    p = await async_playwright().start()
    b = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [pg for pg in b.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url][0]

    res = await page.evaluate('''() => {
        // Find elements with DELIVERABLE AUTOQC
        const all = Array.from(document.querySelectorAll('*'));
        const matches = all.filter(e => (e.innerText || '').trim() === 'DELIVERABLE AUTOQC');
        return matches.map(m => {
            const rect = m.getBoundingClientRect();
            return {
                tag: m.tagName,
                className: m.className,
                rect: { top: rect.top, left: rect.left, width: rect.width, height: rect.height },
                parentTag: m.parentElement ? m.parentElement.tagName : null,
                parentClass: m.parentElement ? m.parentElement.className : null,
                nextSiblingText: m.nextElementSibling ? m.nextElementSibling.innerText.substring(0, 100) : null
            };
        });
    }''')
    print('DELIVERABLE AUTOQC elements:', json.dumps(res, indent=2))

    # Also let's search for how AutoQC API is called:
    # Does Studio have an endpoint like /tasks/{taskId}/autoqc or /autoqc/run or /runs?
    # Let's inspect network / script sources or window object
    api_endpoints = await page.evaluate('''() => {
        // Check window or webpack/next properties
        const keys = Object.keys(window).filter(k => k.toLowerCase().includes('qc') || k.toLowerCase().includes('mercor'));
        return keys;
    }''')
    print('Window keys:', api_endpoints)

    await b.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(inspect_autoqc_dom())
