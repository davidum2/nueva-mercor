import asyncio
import sys
import json
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

DISPUTE_TEXT = "The verifier reasons for Rubric 2 have been updated in the dataset to cite the actual API setters present in the codebase: setDeidentifyTemplate, setStructuredDeidentifyTemplate, and setImageRedactTemplate at patch_a.diff:L81-84 and patch_b.diff:L80-83, removing the outdated reference to setDeidentifyTemplateName."

async def submit_dispute():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    # Find the dispute textarea
    textarea = page.locator('textarea[placeholder*="Why do you dispute"]')
    count = await textarea.count()
    print("Found dispute textarea count:", count)

    if count > 0:
        await page.evaluate('''(text) => {
            const el = document.querySelector('textarea[placeholder*="Why do you dispute"]');
            if (el) {
                const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value").set;
                nativeSetter.call(el, text);
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
            }
        }''', DISPUTE_TEXT)
        print("Filled dispute reason!", flush=True)
        await asyncio.sleep(1)

        # Click Submit button
        submit_btn = page.locator('button:text-is("Submit")')
        count_submit = await submit_btn.count()
        print("Found Submit button count:", count_submit)
        if count_submit > 0:
            await submit_btn.first.click()
            print("Clicked Submit button!", flush=True)
            await asyncio.sleep(3)

    await page.screenshot(path='after_dispute_submitted.png')
    print("Saved after_dispute_submitted.png")

    # Navigate to Navigation tab
    nav_item = page.locator('span:text-is("Navigation")')
    if await nav_item.count() > 0:
        await nav_item.first.click()
        await asyncio.sleep(2)
        await page.evaluate('''() => {
            const el = Array.from(document.querySelectorAll('*')).find(e => e.innerText && e.innerText.startsWith('Before you submit'));
            if (el) el.scrollIntoView({ behavior: 'instant', block: 'start' });
        }''')
        await asyncio.sleep(1)
        await page.screenshot(path='navigation_checklist_dispute_resolved.png')
        print("Saved navigation_checklist_dispute_resolved.png")

    # Inspect all items in checklist
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

        return checklistData;
    }''')
    print("Checklist items status:")
    print(json.dumps(items, indent=2))

    await p.stop()

if __name__ == '__main__':
    asyncio.run(submit_dispute())
