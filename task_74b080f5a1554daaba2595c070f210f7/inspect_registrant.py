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

    registrant_info = await mercor_page.evaluate("""() => {
        const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.trim() === 'Save Changes');
        const key = Object.keys(btn).find(k => k.startsWith('__reactFiber$'));
        let f = btn[key];
        
        let foundD = null;
        while (f) {
            // Check memoizedState or props
            let s = f.memoizedState;
            while (s) {
                if (s.memoizedState && typeof s.memoizedState === 'object') {
                    const obj = s.memoizedState;
                    if (obj.flushAll || obj.registrations || obj.fields) {
                        foundD = {
                            keys: Object.keys(obj),
                            fieldsCount: obj.fields ? Object.keys(obj.fields).length : null,
                            registrationsCount: obj.registrations ? Object.keys(obj.registrations).length : null
                        };
                        break;
                    }
                }
                s = s.next;
            }
            if (foundD) break;
            f = f.return;
        }
        return foundD;
    }""")
    print("Registrant info:", registrant_info)

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
