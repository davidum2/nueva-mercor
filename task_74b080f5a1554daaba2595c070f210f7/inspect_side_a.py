import asyncio
import json
from playwright.async_api import async_playwright

async def run():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    mercor_page = None
    for ctx in browser.contexts:
        for page in ctx.pages:
            if 'mercor.com' in page.url:
                mercor_page = page
                break
        if mercor_page:
            break

    side_a_info = await mercor_page.evaluate("""() => {
        const els = Array.from(document.querySelectorAll('*')).filter(el => {
            const txt = el.innerText || '';
            return txt.includes('Rubric 1 · answer (A)') || txt.includes('Rubric 2 · answer (A)');
        });
        return els.map(el => ({
            tag: el.tagName,
            text: el.innerText.slice(0, 100).replace(/\\n/g, ' ')
        })).slice(0, 10);
    }""")
    print("Side A matches:", json.dumps(side_a_info, indent=2))

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
