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

    # Look at all role="tab"
    tabs = await mercor_page.evaluate("""() => {
        const ts = Array.from(document.querySelectorAll('[role="tab"]'));
        return ts.map(t => ({
            text: t.innerText.trim(),
            state: t.getAttribute('data-state'),
            selected: t.getAttribute('aria-selected')
        }));
    }""")
    print("All tabs on page:", json.dumps(tabs, indent=2))

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
