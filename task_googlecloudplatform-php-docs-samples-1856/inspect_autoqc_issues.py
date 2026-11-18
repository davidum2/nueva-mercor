import asyncio
import json
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def inspect_issues():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    if not task_pages:
        print("No task page found!")
        await p.stop()
        return
    page = task_pages[0]

    # Click Deliverable AutoQC tab
    autoqc_tab = page.locator('button:has-text("Deliverable AutoQC")')
    if await autoqc_tab.count() > 0:
        await autoqc_tab.first.click()
        await asyncio.sleep(2)

    # Click on "Show more" or expand all details if any
    expand_buttons = page.locator('button:has-text("Show more")')
    count = await expand_buttons.count()
    print(f"Found {count} 'Show more' buttons, clicking them...")
    for idx in range(count):
        try:
            await expand_buttons.nth(idx).click()
            await asyncio.sleep(0.3)
        except Exception:
            pass

    # Extract all issues details
    issues_info = await page.evaluate("""() => {
        // Collect all issue cards
        const results = [];
        // Look for cards under Minor issues / Major issues
        const cards = document.querySelectorAll('div[class*="rounded"], div[class*="border"]');
        for (const c of cards) {
            const text = c.innerText || '';
            if ((text.includes('MINOR') || text.includes('MAJOR') || text.includes('Finding #')) && text.length < 2000) {
                results.push(text);
            }
        }
        return {
            totalCards: results.length,
            issues: results
        };
    }""")

    print(f"Extracted {issues_info['totalCards']} cards:")
    for i, issue in enumerate(issues_info['issues']):
        print(f"--- Issue {i+1} ---")
        print(issue)
        print("------------------")

    await page.screenshot(path='autoqc_expanded_issues.png')
    print("Saved autoqc_expanded_issues.png")

    await p.stop()

if __name__ == '__main__':
    asyncio.run(inspect_issues())
