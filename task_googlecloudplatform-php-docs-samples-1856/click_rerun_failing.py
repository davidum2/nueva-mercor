import asyncio
import sys
import time
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def rerun_failing():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    # Find the button 'Rerun 1 failing'
    btn = page.locator('button:has-text("Rerun 1 failing")')
    count = await btn.count()
    print("Found 'Rerun 1 failing' count:", count)

    if count > 0:
        await btn.first.scroll_into_view_if_needed()
        await btn.first.click()
        print("Clicked 'Rerun 1 failing'!", flush=True)

        # Monitor rerun
        start = time.time()
        for i in range(25):
            await asyncio.sleep(3)
            elapsed = int(time.time() - start)
            info = await page.evaluate('''() => {
                const body = document.body.innerText;
                const isRunning = body.includes('AutoQC is running') || body.includes('Compiling') || body.includes('Analyzing');
                const passed = body.match(/(\\d+)\\s*passed/i);
                const major = body.match(/(\\d+)\\s*major/i);
                const minor = body.match(/(\\d+)\\s*minor/i);
                const rerunBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText && b.innerText.includes('Rerun'));
                return {
                    isRunning,
                    passed: passed ? passed[0] : null,
                    major: major ? major[0] : null,
                    minor: minor ? minor[0] : null,
                    rerunText: rerunBtn ? rerunBtn.innerText.trim() : null
                };
            }''')
            print(f"[{elapsed}s] isRunning={info['isRunning']} | passed={info['passed']} | major={info['major']} | minor={info['minor']} | rerunBtn={info['rerunText']}", flush=True)

            if not info['isRunning'] and i >= 3:
                print("Single test case rerun complete! Settling 3s...", flush=True)
                await asyncio.sleep(3)
                break

    await page.screenshot(path='after_rerun_failing.png')
    print("Saved after_rerun_failing.png")

    # Navigate to Submit review -> Navigation
    nav_item = page.locator('span:text-is("Navigation")')
    if await nav_item.count() > 0:
        await nav_item.first.click()
        await asyncio.sleep(2)
        await page.evaluate('''() => {
            const el = Array.from(document.querySelectorAll('*')).find(e => e.innerText && e.innerText.startsWith('Before you submit'));
            if (el) el.scrollIntoView({ behavior: 'instant', block: 'start' });
        }''')
        await asyncio.sleep(1)
        await page.screenshot(path='submit_checklist_after_rerun_failing.png')
        print("Saved submit_checklist_after_rerun_failing.png")

    await p.stop()
    print("Rerun completed successfully!", flush=True)

if __name__ == '__main__':
    asyncio.run(rerun_failing())
