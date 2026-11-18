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

    combos = await mercor_page.evaluate("""() => {
        const btns = Array.from(document.querySelectorAll('[role="combobox"]'));
        return btns.map((b, i) => {
            const parent = b.closest('div')?.parentElement?.parentElement;
            return {
                idx: i,
                text: (b.innerText || '').trim(),
                label: (parent?.innerText || '').slice(0, 80).replace(/\\n/g, ' '),
                id: b.id,
                name: b.getAttribute('name')
            };
        });
    }""")
    print("All comboboxes:")
    for c in combos:
        print(f"  [{c['idx']}] '{c['text']}' -> label: {c['label']}")

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
