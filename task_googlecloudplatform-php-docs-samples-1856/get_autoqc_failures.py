import asyncio
import sys
import json
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def get_failures():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    # Click Deliverable AutoQC
    autoqc_tab = page.locator('span:text-is("Deliverable AutoQC")')
    if await autoqc_tab.count() > 0:
        await autoqc_tab.first.click()
        await asyncio.sleep(1)

    # Scroll down the Deliverable AutoQC card
    await page.evaluate('''() => {
        const header = Array.from(document.querySelectorAll('*')).find(e => e.innerText && e.innerText.includes('DELIVERABLE AUTOQC'));
        if (header) header.scrollIntoView({ behavior: 'instant', block: 'start' });
    }''')
    await asyncio.sleep(1)

    # Click to expand the failed test cases or read the failed items
    details = await page.evaluate('''() => {
        const allText = document.body.innerText;
        
        // Find elements with major, minor, or failed
        const issueElements = Array.from(document.querySelectorAll('div, li, p, span')).filter(el => {
            const t = el.innerText || '';
            return (t.includes('failed') || t.includes('major') || t.includes('failing') || t.includes('Issue')) && t.length < 500;
        }).map(el => el.innerText.trim());

        // Find test cases listed
        const testCases = Array.from(document.querySelectorAll('*')).filter(el => {
            const t = el.innerText || '';
            return t.includes('passed') && (t.includes('Rubric') || t.includes('Score') || t.includes('Dimension'));
        }).map(el => el.innerText.trim());

        return {
            issues: Array.from(new Set(issueElements)).slice(0, 30),
            testCases: Array.from(new Set(testCases)).slice(0, 30)
        };
    }''')

    print("Details found:")
    print(json.dumps(details, indent=2))

    # Take screenshot of the AutoQC card scrolled slightly down
    await page.evaluate('''() => {
        window.scrollBy(0, 300);
    }''')
    await asyncio.sleep(1)
    await page.screenshot(path='autoqc_failures_view.png')
    print("Saved autoqc_failures_view.png")

asyncio.run(get_failures())
