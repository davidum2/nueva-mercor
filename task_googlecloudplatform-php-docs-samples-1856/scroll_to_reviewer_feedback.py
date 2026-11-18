import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def scroll_feedback():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    # Click Reviewer Feedback in sidebar
    rf_tab = page.locator('span:text-is("Reviewer Feedback")')
    if await rf_tab.count() > 0:
        await rf_tab.first.click()
        await asyncio.sleep(1)

    # Scroll middle container to top
    await page.evaluate('''() => {
        const header = Array.from(document.querySelectorAll('*')).find(e => e.innerText && e.innerText.includes('REVIEWER FEEDBACK'));
        if (header) {
            header.scrollIntoView({ behavior: 'instant', block: 'start' });
        }
    }''')
    await asyncio.sleep(1)

    await page.screenshot(path='reviewer_feedback_scrolled_top.png')
    print("Saved reviewer_feedback_scrolled_top.png")

    # Read all text inside the reviewer feedback section
    data = await page.evaluate('''() => {
        const header = Array.from(document.querySelectorAll('*')).find(e => e.innerText && e.innerText.startsWith('REVIEWER FEEDBACK'));
        if (!header) return 'Header not found';
        
        // Find parent container or card
        let p = header;
        while (p && p.tagName !== 'BODY' && !p.className.includes('border') && !p.className.includes('rounded')) {
            p = p.parentElement;
        }
        return p ? p.innerText : header.parentElement.innerText;
    }''')

    print("=== REVIEWER FEEDBACK FULL TEXT ===")
    print(data)
    print("===================================")

    await p.stop()

if __name__ == '__main__':
    asyncio.run(scroll_feedback())
