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
        const cell = document.querySelector('[data-cell="1-1"]');
        if (!cell) return 'no cell';

        const key = Object.keys(cell).find(k => k.startsWith('__reactFiber$'));
        let f = cell[key];
        
        // Invoke onDoubleClick
        if (f.memoizedProps.onDoubleClick) {
            f.memoizedProps.onDoubleClick({
                preventDefault: () => {},
                stopPropagation: () => {}
            });
        }
        return 'called onDoubleClick';
    }""")
    print("Result of onDoubleClick:", res)
    await asyncio.sleep(0.5)

    check = await mercor_page.evaluate("""() => {
        const cell = document.querySelector('[data-cell="1-1"]');
        const ta = cell ? cell.querySelector('textarea, input') : null;
        const globalActive = document.activeElement ? {
            tag: document.activeElement.tagName,
            class: document.activeElement.className,
            val: document.activeElement.value
        } : null;
        return {
            hasInput: !!ta,
            inputTag: ta?.tagName,
            globalActive
        };
    }""")
    print("Check after onDoubleClick:", check)

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
