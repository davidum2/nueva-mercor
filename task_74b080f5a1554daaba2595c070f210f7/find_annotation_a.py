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

    anno_info = await mercor_page.evaluate("""() => {
        const els = Array.from(document.querySelectorAll('*')).filter(el => {
            const t = (el.innerText || '').trim();
            return t === 'ANNOTATION A' || t === 'Annotation A' || t === 'Score rollout A';
        });
        return els.map(e => ({
            tag: e.tagName,
            className: e.className,
            text: e.innerText,
            parentTag: e.parentElement?.tagName,
            parentClass: e.parentElement?.className
        }));
    }""")
    print("Annotation A elements:", json.dumps(anno_info, indent=2))

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
