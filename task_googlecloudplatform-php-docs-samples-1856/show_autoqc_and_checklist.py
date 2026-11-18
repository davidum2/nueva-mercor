import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def show_autoqc_and_checklist():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    # 1. Click 'Deliverable AutoQC' in the left sidebar
    autoqc_tab = page.locator('span:text-is("Deliverable AutoQC")')
    if await autoqc_tab.count() > 0:
        await autoqc_tab.first.click()
        await asyncio.sleep(2)

    # Make sure accordion is open
    content = page.locator('button:has-text("Latest run")')
    if await content.count() == 0:
        header = page.locator('div.cursor-pointer:has-text("DELIVERABLE AUTOQC")')
        if await header.count() > 0:
            await header.first.click()
            await asyncio.sleep(2)

    await page.screenshot(path='autoqc_card_full.png')
    print("Saved autoqc_card_full.png")

    # Extract all text inside the AutoQC section
    autoqc_info = await page.evaluate('''() => {
        const headers = Array.from(document.querySelectorAll('div, button, span')).filter(el => {
            const t = el.innerText || '';
            return t.includes('passed') || t.includes('major') || t.includes('minor') || t.includes('Latest run');
        }).map(el => el.innerText.trim());
        return headers;
    }''')
    print("AutoQC texts:", autoqc_info[:15])

    # 2. Click 'Navigation' in the left sidebar
    nav_tab = page.locator('span:text-is("Navigation")')
    if await nav_tab.count() > 0:
        await nav_tab.first.click()
        await asyncio.sleep(2)

    # Scroll slightly so "Before you submit" card is centered
    await page.evaluate('''() => {
        const el = Array.from(document.querySelectorAll('*')).find(e => e.innerText && e.innerText.startsWith('Before you submit'));
        if (el) el.scrollIntoView({ behavior: 'instant', block: 'start' });
    }''')
    await asyncio.sleep(1)
    await page.screenshot(path='submit_navigation_checklist_perfect.png')
    print("Saved submit_navigation_checklist_perfect.png")

asyncio.run(show_autoqc_and_checklist())
