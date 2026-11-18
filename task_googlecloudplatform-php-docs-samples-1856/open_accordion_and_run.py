import asyncio
import json
import sys
import time
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def expand_and_run():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    # Scroll top
    await page.evaluate("() => window.scrollTo(0,0)")

    # Click DELIVERABLE AUTOQC header to expand
    header = page.locator('div.cursor-pointer:has-text("DELIVERABLE AUTOQC")')
    count = await header.count()
    print("Found header count:", count)
    if count > 0:
        await header.first.scroll_into_view_if_needed()
        await header.first.click()
        print("Clicked header to expand!")
        await asyncio.sleep(2)

    # Click Run AutoQC
    run_btn = page.locator('button:has-text("Run AutoQC")')
    count = await run_btn.count()
    print("Found Run AutoQC count:", count)
    if count > 0:
        await run_btn.first.click()
        print("Clicked Run AutoQC successfully!", flush=True)

        # Monitor run
        start = time.time()
        for cycle in range(45):
            await asyncio.sleep(4)
            info = await page.evaluate("""() => {
                const body = document.body.innerText;
                const isRunning = body.includes('AutoQC is running') || body.includes('Compiling');
                
                const runBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText && (b.innerText.includes('Latest run') || b.innerText.includes('run ·')));
                const runText = runBtn ? runBtn.innerText.trim() : '';

                const passedMatches = body.match(/(\\d+)\\s*passed/i);
                const majorMatches = body.match(/(\\d+)\\s*major/i);
                const minorMatches = body.match(/(\\d+)\\s*minor/i);

                return {
                    isRunning,
                    runText,
                    passed: passedMatches ? passedMatches[0] : null,
                    major: majorMatches ? majorMatches[0] : null,
                    minor: minorMatches ? minorMatches[0] : null
                };
            }""")
            elapsed = int(time.time() - start)
            print(f"[{elapsed}s] isRunning={info['isRunning']} | run={info['runText']} | passed={info['passed']} | major={info['major']} | minor={info['minor']}", flush=True)

            if not info['isRunning'] and cycle >= 2:
                print("AutoQC execution finished! Settling 5s...", flush=True)
                await asyncio.sleep(5)
                break

    await page.screenshot(path='autoqc_100_percent_run_done.png')
    print("Saved autoqc_100_percent_run_done.png", flush=True)

    # Check Submit Review -> Navigation
    nav_btn = page.locator('button[title="Navigation"]')
    if await nav_btn.count() > 0:
        await nav_btn.first.click(force=True)
        await asyncio.sleep(2)
        await page.screenshot(path='final_checklist_after_9_run.png')
        print("Saved final_checklist_after_9_run.png", flush=True)

    await p.stop()
    print("Complete!", flush=True)

if __name__ == '__main__':
    asyncio.run(expand_and_run())
