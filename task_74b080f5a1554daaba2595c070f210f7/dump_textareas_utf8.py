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

    tas = await mercor_page.evaluate(r"""() => {
        const textareas = Array.from(document.querySelectorAll('textarea'));
        return textareas.map((ta, i) => {
            const parent = ta.closest('div')?.parentElement;
            const label = parent ? (parent.querySelector('label')?.innerText || parent.innerText.slice(0, 50)) : '';
            return {
                idx: i,
                label: label.split('\n').join(' '),
                val: ta.value
            };
        });
    }""")
    
    with open('all_textareas_dump.json', 'w', encoding='utf-8') as f:
        json.dump(tas, f, indent=2, ensure_ascii=False)

    print(f"Dumped {len(tas)} textareas to all_textareas_dump.json")

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
