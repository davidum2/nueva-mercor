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

    res = await mercor_page.evaluate("""() => {
        // Let's find all labels and form controls currently visible
        const controls = [];
        const labels = Array.from(document.querySelectorAll('label, [class*="label"], h3, h4'));
        for (const l of labels) {
            const txt = (l.innerText || '').trim();
            if (txt.includes('Rubric') || txt.includes('rubric') || txt.includes('Dimension') || txt.includes('reason')) {
                controls.push({
                    text: txt.replace(/\\n/g, ' '),
                    tag: l.tagName
                });
            }
        }
        return controls;
    }""")
    print(f"Total controls found: {len(res)}")
    for i, c in enumerate(res):
        print(f"  {i}: {c['tag']}: {c['text']}")

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
