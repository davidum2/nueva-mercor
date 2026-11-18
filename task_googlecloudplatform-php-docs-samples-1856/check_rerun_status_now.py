import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def check():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    # Check AutoQC text
    autoqc_tab = page.locator('span:text-is("Deliverable AutoQC")')
    if await autoqc_tab.count() > 0:
        await autoqc_tab.first.click()
        await asyncio.sleep(2)

    card_text = await page.evaluate('''() => {
        const body = document.body.innerText;
        const autoqcCard = Array.from(document.querySelectorAll('*'))
            .filter(el => el.innerText && el.innerText.includes('DELIVERABLE AUTOQC') && el.innerText.includes('check your work'))[0];
        return autoqcCard ? autoqcCard.innerText : body.slice(0, 2000);
    }''')
    print("=== AUTOQC CARD TEXT ===")
    print(card_text)
    print("=========================")

    await page.screenshot(path='autoqc_card_now.png')
    print("Saved autoqc_card_now.png")

    # Check Navigation tab
    nav_tab = page.locator('span:text-is("Navigation")')
    if await nav_tab.count() > 0:
        await nav_tab.first.click()
        await asyncio.sleep(2)
        await page.evaluate('''() => {
            const el = Array.from(document.querySelectorAll('*')).find(e => e.innerText && e.innerText.startsWith('Before you submit'));
            if (el) el.scrollIntoView({ behavior: 'instant', block: 'start' });
        }''')
        await asyncio.sleep(1)
        await page.screenshot(path='navigation_checklist_now.png')
        print("Saved navigation_checklist_now.png")

    await p.stop()

if __name__ == '__main__':
    asyncio.run(check())
