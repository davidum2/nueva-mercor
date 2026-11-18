import asyncio
import sys
import json
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def verify():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    print("Reloading page...", flush=True)
    await page.reload(wait_until='domcontentloaded')
    await asyncio.sleep(5)

    # Click Navigation in the left tabs under Submit review
    nav_item = page.locator('span:text-is("Navigation")')
    if await nav_item.count() > 0:
        await nav_item.first.click()
        await asyncio.sleep(2)
        await page.evaluate('''() => {
            const el = Array.from(document.querySelectorAll('*')).find(e => e.innerText && e.innerText.startsWith('Before you submit'));
            if (el) el.scrollIntoView({ behavior: 'instant', block: 'start' });
        }''')
        await asyncio.sleep(1)
        await page.screenshot(path='final_navigation_checklist_success.png')
        print("Saved final_navigation_checklist_success.png")

    # Read all checklist items status from React Fiber
    items = await page.evaluate('''() => {
        const item = Array.from(document.querySelectorAll('li')).find(l => l.innerText && l.innerText.includes('AutoQC failures resolved'));
        if (!item) return { error: "li not found" };

        const k = Object.keys(item).find(key => key.startsWith('__reactFiber$'));
        let f = item[k];
        let checklistData = null;
        while (f && !checklistData) {
            if (f.memoizedProps && f.memoizedProps.items) {
                checklistData = f.memoizedProps.items;
            }
            f = f.return;
        }

        const submitBtn = document.querySelector('button:has-text("Submit for Final QC")');

        return {
            checklist: checklistData,
            submitBtn: submitBtn ? {
                text: submitBtn.innerText,
                disabled: submitBtn.disabled
            } : null
        };
    }''')

    print("Final Verification Checklist:")
    print(json.dumps(items, indent=2))

    await p.stop()

if __name__ == '__main__':
    asyncio.run(verify())
