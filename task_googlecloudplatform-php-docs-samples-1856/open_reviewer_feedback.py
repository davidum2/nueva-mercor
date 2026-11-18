import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def open_feedback():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    # Find REVIEWER FEEDBACK header
    header = page.locator('div.cursor-pointer:has-text("REVIEWER FEEDBACK")')
    count = await header.count()
    print("Found header count:", count)
    if count > 0:
        await header.first.scroll_into_view_if_needed()
        await header.first.click()
        await asyncio.sleep(2)

    await page.screenshot(path='reviewer_feedback_expanded.png')
    print("Saved reviewer_feedback_expanded.png")

    # Extract all text inside REVIEWER FEEDBACK section
    text = await page.evaluate('''() => {
        const sections = Array.from(document.querySelectorAll('*')).filter(el => {
            const t = el.innerText || '';
            return t.startsWith('REVIEWER FEEDBACK') || t.includes('Feedback for writer') || t.includes('Adjudication rationale');
        });
        return sections.map(s => s.innerText);
    }''')

    print("=== REVIEWER FEEDBACK CONTENT ===")
    for s in text:
        if len(s) < 3000:
            print(s)
            print("=" * 40)

    await p.stop()

if __name__ == '__main__':
    asyncio.run(open_feedback())
