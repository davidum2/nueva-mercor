import asyncio
import sys
import json
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def inspect():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    res = await page.evaluate('''() => {
        // Find Navigation list
        const items = Array.from(document.querySelectorAll('*')).filter(el => el.innerText && el.innerText.startsWith('AutoQC failures resolved'));
        if (!items.length) return { error: "Item not found" };

        const target = items[0];
        const k = Object.keys(target).find(key => key.startsWith('__reactFiber$'));
        let f = target[k];

        const hierarchy = [];
        while (f && hierarchy.length < 15) {
            if (f.memoizedProps) {
                const keys = Object.keys(f.memoizedProps);
                const interesting = {};
                for (const key of keys) {
                    const val = f.memoizedProps[key];
                    if (typeof val === 'boolean' || typeof val === 'string' || typeof val === 'number') {
                        interesting[key] = val;
                    }
                }
                hierarchy.push({
                    type: typeof f.type === 'string' ? f.type : (f.type?.name || 'Component'),
                    props: interesting
                });
            }
            f = f.return;
        }

        return hierarchy;
    }''')

    print("Checklist Item Fiber Hierarchy:")
    print(json.dumps(res, indent=2))

    await p.stop()

if __name__ == '__main__':
    asyncio.run(inspect())
