import asyncio
import json
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def show_autoqc():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    if not task_pages:
        print("No task page found!")
        await p.stop()
        return
    page = task_pages[0]

    # Press Escape to close any menu
    await page.keyboard.press("Escape")
    await asyncio.sleep(0.5)

    # Scroll Deliverable AutoQC section into view
    autoqc_sec = page.locator('text=DELIVERABLE AUTOQC')
    if await autoqc_sec.count() > 0:
        await autoqc_sec.first.scroll_into_view_if_needed()
        await asyncio.sleep(1)

    # Click on "Deliverable AutoQC" in the left sidebar to focus the tab cleanly
    sidebar_autoqc = page.locator('button:has-text("Deliverable AutoQC")')
    if await sidebar_autoqc.count() > 0:
        await sidebar_autoqc.first.click()
        await asyncio.sleep(1)

    # Extract all issues under Deliverable AutoQC
    info = await page.evaluate("""() => {
        // Find all cards with 'MINOR' or 'MAJOR'
        const cards = [];
        document.querySelectorAll('div').forEach(d => {
            const t = d.innerText || '';
            if (t.includes('Finding #') && (t.includes('MINOR') || t.includes('MAJOR'))) {
                // Check if already captured in parent
                cards.push(t);
            }
        });

        // Also find the summary block
        const issuesHeader = Array.from(document.querySelectorAll('*')).find(el => el.innerText && (el.innerText.startsWith('Minor issues') || el.innerText.startsWith('Major issues')));

        return {
            cards: cards.slice(0, 10),
            pageTextSnippet: document.body.innerText.substring(document.body.innerText.indexOf('DELIVERABLE AUTOQC'), document.body.innerText.indexOf('DELIVERABLE AUTOQC') + 2500)
        };
    }""")

    print("Snippet from DELIVERABLE AUTOQC:")
    print(info['pageTextSnippet'])
    print("Cards found:", len(info['cards']))
    for c in info['cards']:
        print("CARD:", c[:200])

    await page.screenshot(path='autoqc_section_clean.png')
    print("Saved autoqc_section_clean.png")

    await p.stop()

if __name__ == '__main__':
    asyncio.run(show_autoqc())
