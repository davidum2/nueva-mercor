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

    handlers = await mercor_page.evaluate("""() => {
        const cell = document.querySelector('[data-cell="1-1"]');
        if (!cell) return null;

        // Traverse React fiber
        const key = Object.keys(cell).find(k => k.startsWith('__reactFiber$'));
        let f = cell[key];
        const res = [];
        while (f) {
            const props = f.memoizedProps || {};
            const onKeys = Object.keys(props).filter(k => k.startsWith('on') || k.includes('edit') || k.includes('change') || k.includes('Click'));
            if (onKeys.length > 0) {
                res.push({
                    type: typeof f.type === 'string' ? f.type : (f.type?.displayName || f.type?.name || 'Component'),
                    keys: onKeys,
                    // If there's an onChange or onEdit or onValueChange or updateCell
                    handlers: onKeys.map(k => `${k}: ${typeof props[k]}`)
                });
            }
            f = f.return;
        }
        return res;
    }""")
    
    import json
    print("Fiber hierarchy handlers:")
    print(json.dumps(handlers, indent=2))

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
