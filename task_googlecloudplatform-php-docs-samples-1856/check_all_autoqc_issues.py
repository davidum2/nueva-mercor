import asyncio
import json
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def get_all_issues():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]
    
    # Click 'All' filter button
    all_btn = page.locator('button:has-text("All")')
    if await all_btn.count() > 0:
        await all_btn.first.click()
        await asyncio.sleep(1)

    # Expand all 'Show more' buttons
    show_mores = await page.locator('button:has-text("Show more")').all()
    for sm in show_mores:
        try:
            await sm.click()
        except:
            pass
    await asyncio.sleep(1)

    cards = await page.evaluate("""() => {
        const results = [];
        const headings = Array.from(document.querySelectorAll('div[class*="border rounded"]'));
        for (const h of headings) {
            const txt = h.innerText.trim();
            if (txt.includes('MAJOR') || txt.includes('MINOR') || txt.includes('Finding') || txt.includes('Actually Audited') || txt.includes('Matches') || txt.includes('Rubric')) {
                results.push(txt);
            }
        }
        return results;
    }""")

    print(f"Total issue cards found: {len(cards)}")
    for i, c in enumerate(cards):
        print(f"\n==================== ISSUE {i+1} ====================")
        print(c)

    await p.stop()

if __name__ == '__main__':
    asyncio.run(get_all_issues())
