import asyncio
import json
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def check():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    autoqc_tab = page.locator('span:has-text("Deliverable AutoQC")')
    if await autoqc_tab.count() > 0:
        await autoqc_tab.first.click()
        await asyncio.sleep(2)

    buttons = await page.evaluate('''() => {
        return Array.from(document.querySelectorAll('button')).map(b => ({
            text: b.innerText,
            disabled: b.disabled
        })).filter(b => b.text && (b.text.includes('AutoQC') || b.text.includes('Run') || b.text.includes('Rerun')));
    }''')
    print("Buttons on Deliverable AutoQC:")
    print(json.dumps(buttons, indent=2))

    # Also check the current AutoQC screen text
    tab_text = await page.evaluate('''() => {
        const el = document.querySelector('main') || document.body;
        return el.innerText.slice(0, 1500);
    }''')
    print("\nPage text excerpt:\n", tab_text[:500])

    await p.stop()

if __name__ == '__main__':
    asyncio.run(check())
