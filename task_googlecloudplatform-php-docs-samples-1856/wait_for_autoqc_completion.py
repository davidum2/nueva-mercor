import asyncio
import json
import sys
import time
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def wait_autoqc():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    if not task_pages:
        print("No task page found!")
        await p.stop()
        return
    page = task_pages[0]

    # Click on Deliverable AutoQC tab first
    autoqc_tab = page.locator('button:has-text("Deliverable AutoQC")')
    if await autoqc_tab.count() > 0:
        await autoqc_tab.first.click()
        await asyncio.sleep(2)

    print("Monitoring AutoQC run completion...", flush=True)

    start_time = time.time()
    for cycle in range(40): # up to 200 seconds
        state = await page.evaluate("""() => {
            const body = document.body.innerText;
            const isRunning = body.includes('AutoQC is running') || body.includes('Running AutoQC...');
            
            // Look for progress indicators
            let progress = '';
            if (body.includes('Analyzing')) {
                const match = body.match(/Analyzing \\d+\\/\\d+/);
                if (match) progress = match[0];
            } else if (body.includes('Compiling')) {
                progress = 'Compiling';
            } else if (body.includes('Preparing')) {
                progress = 'Preparing';
            } else if (body.includes('Staging context')) {
                progress = 'Staging context';
            }

            // Look for run time dropdown
            const runBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText && b.innerText.includes('Latest run') || b.innerText.includes('run ·'));
            const latestRunText = runBtn ? runBtn.innerText.trim() : '';

            // Look for tests summary
            const passedMatches = body.match(/(\\d+)\\s*passed/i);
            const majorMatches = body.match(/(\\d+)\\s*major/i);
            const minorMatches = body.match(/(\\d+)\\s*minor/i);

            return {
                isRunning,
                progress,
                latestRunText,
                passed: passedMatches ? passedMatches[0] : null,
                major: majorMatches ? majorMatches[0] : null,
                minor: minorMatches ? minorMatches[0] : null
            };
        }""")

        elapsed = int(time.time() - start_time)
        print(f"[{elapsed}s] Running: {state['isRunning']} | Progress: {state['progress']} | Run: {state['latestRunText']} | Passed: {state['passed']} | Major: {state['major']} | Minor: {state['minor']}", flush=True)

        if not state['isRunning'] and cycle >= 2:
            print("AutoQC execution finished! Settling for 5 seconds...", flush=True)
            await asyncio.sleep(5)
            break

        await asyncio.sleep(5)

    # Capture screenshots of Deliverable AutoQC
    await page.screenshot(path='autoqc_completed_run.png')
    print("Saved autoqc_completed_run.png", flush=True)

    # Also check Submit review -> Navigation checklist
    nav_item = page.locator('button:has-text("Navigation")')
    if await nav_item.count() > 0:
        await nav_item.first.click()
        await asyncio.sleep(2)
        await page.screenshot(path='submit_navigation_checklist.png')
        print("Saved submit_navigation_checklist.png", flush=True)

    await p.stop()
    print("Done waiting!", flush=True)

if __name__ == '__main__':
    asyncio.run(wait_autoqc())
