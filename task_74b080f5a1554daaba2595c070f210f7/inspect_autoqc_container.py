import asyncio
import json
from playwright.async_api import async_playwright

async def run():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    ctx = browser.contexts[0]
    task_page = None
    for pg in ctx.pages:
        if 'task_74b080f5a1554daaba2595c070f210f7/?' in pg.url:
            task_page = pg
            break

    info = await task_page.evaluate("""() => {
        // Find text containing DELIVERABLE AUTOQC
        const all = Array.from(document.querySelectorAll('*'));
        const el = all.find(e => (e.innerText || '').trim() === 'DELIVERABLE AUTOQC');
        if (!el) return { found: false };
        
        let p = el.parentElement;
        for (let i = 0; i < 5 && p; i++) {
            const btns = Array.from(p.querySelectorAll('button')).map(b => b.innerText.trim());
            if (btns.length > 0) {
                return { found: true, parentTag: p.tagName, btns };
            }
            p = p.parentElement;
        }
        return { found: true, noBtnsInParent: true };
    }""")
    print("AutoQC container info:", json.dumps(info, indent=2))

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
