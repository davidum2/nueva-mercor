import asyncio
import json
from playwright.async_api import async_playwright

async def inspect():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    old_rubric = [pg for pg in browser.contexts[0].pages if 'task_74b' in pg.url and '/rubric/' in pg.url][0]
    
    # Check if there is an API request that fetched the rubric
    res = await old_rubric.evaluate('''() => {
        // Search all react fibers on page for an array of 15 items
        const all = Array.from(document.querySelectorAll('*'));
        let found = [];
        for (let el of all) {
            const k = Object.keys(el).find(key => key.startsWith('__reactFiber$'));
            if (!k) continue;
            let f = el[k];
            let depth = 0;
            while (f && depth < 30) {
                const s = f.memoizedState;
                const p = f.memoizedProps;
                for (let obj of [s, p]) {
                    if (!obj) continue;
                    for (let key of Object.keys(obj)) {
                        const val = obj[key];
                        if (Array.isArray(val) && val.length === 15 && typeof val[0] === 'object') {
                            found.push({
                                tag: el.tagName,
                                key,
                                sampleItem: val[0],
                                len: val.length
                            });
                        }
                    }
                }
                f = f.return;
                depth++;
            }
            if (found.length > 0) break;
        }
        return found;
    }''')

    print("Found rubric array in React state:")
    print(json.dumps(res, indent=2))

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(inspect())
