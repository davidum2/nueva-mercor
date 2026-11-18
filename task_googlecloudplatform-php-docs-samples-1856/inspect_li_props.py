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
        const item = Array.from(document.querySelectorAll('li')).find(l => l.innerText && l.innerText.includes('AutoQC failures resolved'));
        if (!item) return { error: "li not found" };

        const k = Object.keys(item).find(key => key.startsWith('__reactFiber$'));
        let f = item[k];

        // Find the component that created this li
        let curr = f;
        let checklistData = null;
        while (curr && !checklistData) {
            if (curr.memoizedProps && (curr.memoizedProps.items || curr.memoizedProps.checks || curr.memoizedProps.failures || curr.memoizedProps.audit)) {
                checklistData = {
                    keys: Object.keys(curr.memoizedProps),
                    props: curr.memoizedProps
                };
            }
            curr = curr.return;
        }

        return {
            liProps: f ? f.memoizedProps : null,
            parentData: checklistData
        };
    }''')

    print("Checklist Item Fiber:")
    print(json.dumps(res, indent=2, default=str))

    await p.stop()

if __name__ == '__main__':
    asyncio.run(inspect())
