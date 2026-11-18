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

    # Click cell 1-1
    res = await mercor_page.evaluate("""() => {
        const cell = document.querySelector('[data-cell="1-1"]');
        if (!cell) return null;
        
        // Let's inspect React Fiber for event handlers
        const key = Object.keys(cell).find(k => k.startsWith('__reactFiber$'));
        let f = cell[key];
        let handlers = [];
        while (f) {
            if (f.memoizedProps) {
                const h = Object.keys(f.memoizedProps).filter(k => k.startsWith('on'));
                if (h.length > 0) handlers.push({ type: f.type ? f.type.name || f.type : '', handlers: h });
            }
            f = f.return;
        }
        
        // Try double click
        cell.dispatchEvent(new MouseEvent('dblclick', { bubbles: true }));
        
        return {
            handlers,
            hasInputAfterDblClick: !!cell.querySelector('input, textarea, select'),
            cellHTML: cell.innerHTML
        };
    }""")
    print("Dblclick cell 1-1:", res)

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
