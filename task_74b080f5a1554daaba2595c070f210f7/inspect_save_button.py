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

    # Look at Save Changes button Fiber
    save_btn_info = await mercor_page.evaluate("""() => {
        const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.trim() === 'Save Changes');
        if (!btn) return 'no save btn';
        
        const key = Object.keys(btn).find(k => k.startsWith('__reactFiber$'));
        let f = btn[key];
        const callers = [];
        while (f) {
            if (f.memoizedProps && f.memoizedProps.onClick) {
                callers.push({
                    type: f.type?.name || typeof f.type,
                    onClickStr: f.memoizedProps.onClick.toString().slice(0, 200)
                });
            }
            f = f.return;
        }
        return callers;
    }""")
    print("Save btn callers:", json.dumps(save_btn_info, indent=2))

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
