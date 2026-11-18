import asyncio
import json
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def inspect():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    # Scroll Deliverable AutoQC into view
    await page.evaluate('''() => {
        const el = Array.from(document.querySelectorAll('*')).find(e => e.innerText && e.innerText.startsWith('DELIVERABLE AUTOQC'));
        if (el) el.scrollIntoView({ behavior: 'instant', block: 'start' });
    }''')
    await asyncio.sleep(1)
    await page.screenshot(path='autoqc_scroll_results.png')
    print("Saved autoqc_scroll_results.png")

    # Navigate to Navigation tab under Submit review
    nav_tab = page.locator('span:text-is("Navigation")')
    if await nav_tab.count() > 0:
        await nav_tab.first.click()
        await asyncio.sleep(2)
        await page.evaluate('''() => {
            const el = Array.from(document.querySelectorAll('*')).find(e => e.innerText && e.innerText.startsWith('Before you submit'));
            if (el) el.scrollIntoView({ behavior: 'instant', block: 'start' });
        }''')
        await asyncio.sleep(1)
        await page.screenshot(path='final_navigation_checklist_after_run.png')
        print("Saved final_navigation_checklist_after_run.png")

    # Inspect the checklist items from DOM
    checklist_status = await page.evaluate('''() => {
        const listItems = Array.from(document.querySelectorAll('li')).filter(l => {
            const t = l.innerText || '';
            return t.includes('Length limits') || t.includes('AutoQC failures') || t.includes('AutoQC up to date');
        });
        const submitBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText && b.innerText.includes('Submit for Final QC'));

        return {
            items: listItems.map(l => ({
                text: l.innerText.replace(/\\n/g, ' ').trim(),
                has_green_check: !!l.querySelector('svg[class*="text-emerald"], svg[class*="text-green"], [data-state="checked"]') || l.innerHTML.includes('text-emerald') || l.innerHTML.includes('text-green') || l.innerHTML.includes('stroke="#10b981"') || l.innerHTML.includes('currentColor')
            })),
            submitBtn: submitBtn ? {
                text: submitBtn.innerText,
                disabled: submitBtn.disabled
            } : null
        };
    }''')
    print("Checklist status:")
    print(json.dumps(checklist_status, indent=2))

    await p.stop()

if __name__ == '__main__':
    asyncio.run(inspect())
