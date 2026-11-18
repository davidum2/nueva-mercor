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

    tabs = await mercor_page.evaluate("""() => {
        const buttons = Array.from(document.querySelectorAll('button, [role="tab"]'));
        return buttons.map(b => ({
            text: (b.innerText || '').trim().replace(/\\n/g, ' '),
            role: b.getAttribute('role'),
            dataState: b.getAttribute('data-state'),
            ariaSelected: b.getAttribute('aria-selected')
        })).filter(b => b.text.includes('AGENT') || b.text.includes('TRAJECTORY') || b.text.includes('MODEL') || b.text.includes('Model') || b.text.includes('Side') || b.text.includes('Evaluation'));
    }""")
    print("Model/Side tabs:", json.dumps(tabs, indent=2))

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
