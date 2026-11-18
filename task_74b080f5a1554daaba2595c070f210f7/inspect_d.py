import asyncio
import json
from playwright.async_api import async_playwright

async def inspect_d():
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
        const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.trim() === 'Save Changes');
        const key = Object.keys(btn).find(k => k.startsWith('__reactFiber$'));
        let f = btn[key];
        
        while (f) {
            if (f.memoizedProps?.onClick) {
                // Check props of parent components
                if (f.memoizedProps.registrant || f.memoizedProps.value?.flushAll) {
                    return {
                        found: true,
                        props: Object.keys(f.memoizedProps),
                        valueKeys: f.memoizedProps.value ? Object.keys(f.memoizedProps.value) : null
                    };
                }
            }
            f = f.return;
        }
        return { found: false };
    }""")
    print("Found registrant in Fiber tree:", res)

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(inspect_d())
