import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def inspect():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    # First click Rubric tab to see the middle panel with DELIVERABLE AUTOQC
    rubric_tab = page.locator('span:text-is("Rubric")')
    if await rubric_tab.count() > 0:
        await rubric_tab.first.click()
        await asyncio.sleep(1)

    # Click DELIVERABLE AUTOQC header to expand
    header = page.locator('div.cursor-pointer:has-text("DELIVERABLE AUTOQC")')
    if await header.count() > 0:
        await header.first.scroll_into_view_if_needed()
        await header.first.click()
        await asyncio.sleep(2)
        await page.screenshot(path='autoqc_expanded_view.png')
        print("Saved autoqc_expanded_view.png")

    # Read AutoQC text summary
    summary = await page.evaluate('''() => {
        const body = document.body.innerText;
        const autoqcText = Array.from(document.querySelectorAll('*'))
            .filter(el => el.innerText && el.innerText.includes('passed') && el.innerText.includes('Run AutoQC'))
            .map(el => el.innerText.slice(0, 500))[0] || '';
        return {
            passed: body.match(/(\\d+)\\s*passed/i) ? body.match(/(\\d+)\\s*passed/i)[0] : null,
            major: body.match(/(\\d+)\\s*major/i) ? body.match(/(\\d+)\\s*major/i)[0] : null,
            minor: body.match(/(\\d+)\\s*minor/i) ? body.match(/(\\d+)\\s*minor/i)[0] : null,
            runs: Array.from(document.querySelectorAll('button')).filter(b => b.innerText && (b.innerText.includes('Latest run') || b.innerText.includes('run ·'))).map(b => b.innerText.trim())
        };
    }''')
    print("AutoQC summary:", summary)

    # Click Navigation in the left tabs under Submit review
    nav_item = page.locator('span:text-is("Navigation")')
    if await nav_item.count() > 0:
        await nav_item.first.click()
        await asyncio.sleep(2)
        # Scroll the middle panel down
        await page.evaluate('''() => {
            const containers = Array.from(document.querySelectorAll('div')).filter(d => d.scrollHeight > d.clientHeight);
            for (const c of containers) {
                if (c.innerText.includes('Before you submit') || c.innerText.includes('AutoQC failures resolved')) {
                    c.scrollTop = c.scrollHeight;
                }
            }
        }''')
        await asyncio.sleep(1)
        await page.screenshot(path='navigation_checklist_scrolled.png')
        print("Saved navigation_checklist_scrolled.png")

    # Read checklist items status
    checklist_status = await page.evaluate('''() => {
        const items = Array.from(document.querySelectorAll('li, div')).filter(el => {
            return el.innerText && (
                el.innerText.includes('Length limits') ||
                el.innerText.includes('AutoQC failures') ||
                el.innerText.includes('AutoQC up to date') ||
                el.innerText.includes('Rubric count') ||
                el.innerText.includes('Before you submit')
            );
        }).map(el => el.innerText.split('\\n')[0]);
        return Array.from(new Set(items));
    }''')
    print("Checklist items:", checklist_status)

asyncio.run(inspect())
