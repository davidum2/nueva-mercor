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

    node_info = await mercor_page.evaluate("""() => {
        const els = Array.from(document.querySelectorAll('*')).filter(el => {
            return (el.innerText || '').trim() === 'RUBRIC' && el.children.length === 0;
        });
        
        if (els.length === 0) return { found: false };
        
        const target = els[0];
        target.scrollIntoView();
        
        let p = target.parentElement;
        const parents = [];
        for (let i = 0; i < 6 && p; i++) {
            parents.push({
                tag: p.tagName,
                className: p.className,
                childrenCount: p.children.length,
                innerHTML: p.innerHTML.substring(0, 300)
            });
            p = p.parentElement;
        }
        
        return {
            found: true,
            tag: target.tagName,
            rect: target.getBoundingClientRect(),
            parents
        };
    }""")
    print("RUBRIC node info:", node_info)

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
