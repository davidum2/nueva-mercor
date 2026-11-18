import asyncio
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

    res = await mercor_page.evaluate("""() => {
        // Find all labels, buttons, or inputs currently visible
        const controls = Array.from(document.querySelectorAll('label, [role="combobox"], textarea, h3, h4, [class*="title"]')).map(el => {
            return {
                tag: el.tagName,
                text: (el.innerText || el.value || '').trim().replace(/\\n/g, ' ').slice(0, 80)
            };
        });
        return controls;
    }""")
    
    print(f"Total controls: {len(res)}")
    for i, c in enumerate(res[50:], 50):
        print(f"  [{i}] {c['tag']}: {c['text']}")

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
