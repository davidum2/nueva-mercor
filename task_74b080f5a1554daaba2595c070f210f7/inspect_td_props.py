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

    props_info = await mercor_page.evaluate("""() => {
        const cell = document.querySelector('[data-cell="1-1"]');
        if (!cell) return null;

        const key = Object.keys(cell).find(k => k.startsWith('__reactFiber$'));
        let f = cell[key];
        const tdProps = {};
        for (const k in f.memoizedProps) {
            tdProps[k] = typeof f.memoizedProps[k] === 'function' ? 'function' : f.memoizedProps[k];
        }

        // Look at parent component props
        let parentProps = {};
        let curr = f;
        while (curr) {
            if (curr.type && curr.type.name === 'eD' || (curr.memoizedProps && curr.memoizedProps.data)) {
                for (const k in curr.memoizedProps) {
                    const v = curr.memoizedProps[k];
                    parentProps[k] = typeof v === 'function' ? 'function' : (typeof v === 'object' ? Object.keys(v || {}) : v);
                }
                break;
            }
            curr = curr.return;
        }

        return { tdProps, parentProps };
    }""")

    print(json.dumps(props_info, indent=2))

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
