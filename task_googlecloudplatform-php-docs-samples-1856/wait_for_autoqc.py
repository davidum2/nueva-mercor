import asyncio
import sys
import time
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def wait_autoqc():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    for i in range(20):
        info = await page.evaluate('''() => {
            const body = document.body.innerText;
            const isRunning = body.includes('AutoQC is running') || body.includes('Compiling') || body.includes('Analyzing');
            const passedMatches = body.match(/(\d+)\s*passed/i);
            const majorMatches = body.match(/(\d+)\s*major/i);
            const minorMatches = body.match(/(\d+)\s*minor/i);
            const latestBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText && (b.innerText.includes('Latest run') || b.innerText.includes('run ·')));
            return {
                isRunning,
                passed: passedMatches ? passedMatches[0] : null,
                major: majorMatches ? majorMatches[0] : null,
                minor: minorMatches ? minorMatches[0] : null,
                latestBtnText: latestBtn ? latestBtn.innerText.trim() : null
            };
        }''')
        print(f"[{i*5}s] isRunning={info['isRunning']} | passed={info['passed']} | major={info['major']} | minor={info['minor']} | btn={info['latestBtnText']}", flush=True)
        if not info['isRunning']:
            print("AutoQC completed!")
            break
        await asyncio.sleep(5)

    # Click Deliverable AutoQC tab or scroll to see results
    autoqc_nav = page.locator('span:text-is("Deliverable AutoQC")')
    if await autoqc_nav.count() > 0:
        await autoqc_nav.first.click()
        await asyncio.sleep(2)

    await page.screenshot(path='autoqc_result_screen.png')
    print("Saved autoqc_result_screen.png")

    # Navigate to Navigation tab under Submit review
    nav_tab = page.locator('span:text-is("Navigation")')
    if await nav_tab.count() > 0:
        await nav_tab.first.click()
        await asyncio.sleep(2)
        await page.screenshot(path='submit_navigation_checklist_latest.png')
        print("Saved submit_navigation_checklist_latest.png")

asyncio.run(wait_autoqc())
