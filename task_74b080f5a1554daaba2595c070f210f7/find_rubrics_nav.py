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

    rubric_elements = await mercor_page.evaluate("""() => {
        const els = Array.from(document.querySelectorAll('*')).filter(el => {
            const t = (el.innerText || '').trim();
            return t.toLowerCase().includes('rubric') && el.children.length === 0;
        });
        return els.map((el, i) => ({
            i,
            text: el.innerText.trim(),
            tagName: el.tagName,
            className: el.className,
            parentClass: el.parentElement ? el.parentElement.className : '',
            rect: el.getBoundingClientRect()
        }));
    }""")
    print("Found rubric elements:", len(rubric_elements))
    for el in rubric_elements:
        print(f"#{el['i']}: '{el['text']}' [{el['tagName']}] y={el['rect']['y']} h={el['rect']['height']}")

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
