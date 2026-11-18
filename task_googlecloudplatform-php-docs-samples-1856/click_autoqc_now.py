import asyncio
import json
import sys
import time
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def run_now():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    # Expand DELIVERABLE AUTOQC
    res = await page.evaluate("""() => {
        const div = Array.from(document.querySelectorAll('div')).find(d => {
            return d.className.includes('cursor-pointer') && d.innerText && d.innerText.trim().startsWith('DELIVERABLE AUTOQC');
        });
        if (div) {
            div.click();
            return { ok: true };
        }
        return { ok: false };
    }""")
    print("Expanded DELIVERABLE AUTOQC:", res)
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
        for c in range(45):
            await asyncio.sleep(4)
            info = await page.evaluate("""() => {
                const body = document.body.innerText;
                const isRunning = body.includes('AutoQC is running') || body.includes('Compiling');
                
                const runBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText && (b.innerText.includes('Latest run') || b.innerText.includes('run ·')));
                const runText = runBtn ? runBtn.innerText.trim() : '';

                const passed = body.match(/(\\d+)\\s*passed/i);
                const major = body.match(/(\\d+)\\s*major/i);
                const minor = body.match(/(\\d+)\\s*minor/i);

                return { isRunning, runText, passed: passed ? passed[0] : null, major: major ? major[0] : null, minor: minor ? minor[0] : null };
            }""")
            elapsed = int(time.time() - start)
            print(f"[{elapsed}s] isRunning={info['isRunning']} | run={info['runText']} | passed={info['passed']} | major={info['major']} | minor={info['minor']}", flush=True)

            if not info['isRunning'] and c >= 2:
                print("AutoQC finished! Waiting 5s...", flush=True)
                await asyncio.sleep(5)
                break

    await page.screenshot(path='autoqc_9_rubrics_result.png')
    print("Saved autoqc_9_rubrics_result.png", flush=True)

    # Navigate to submit review tab
    nav_btn = page.locator('button[title="Navigation"]')
    if await nav_btn.count() > 0:
        await nav_btn.first.click(force=True)
        await asyncio.sleep(2)
        await page.screenshot(path='final_navigation_checklist_9.png')
        print("Saved final_navigation_checklist_9.png", flush=True)

    await p.stop()
    print("Complete!", flush=True)

if __name__ == '__main__':
    asyncio.run(run_now())
