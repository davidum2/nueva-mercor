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

    # Find the header with text 'DELIVERABLE AUTOQC'
    header = page.locator('div.cursor-pointer:has-text("DELIVERABLE AUTOQC")')
    count = await header.count()
    print("Found DELIVERABLE AUTOQC header count:", count)
    if count > 0:
        await header.first.click()
        print("Clicked header to expand!")
        await asyncio.sleep(2)

    # Check for Run AutoQC button
    run_btn = page.locator('button:has-text("Run AutoQC")')
    btn_count = await run_btn.count()
    print("Found Run AutoQC button count:", btn_count)

    if btn_count > 0:
        await run_btn.first.click()
        print("Clicked Run AutoQC button successfully!", flush=True)

        # Monitor execution
        print("Monitoring AutoQC run...", flush=True)
        start = time.time()
        for cycle in range(40):
            await asyncio.sleep(4)
            info = await page.evaluate("""() => {
                const body = document.body.innerText;
                const isRunning = body.includes('AutoQC is running') || body.includes('Running AutoQC...');
                
                let prog = '';
                if (body.includes('Analyzing')) {
                    const m = body.match(/Analyzing \\d+\\/\\d+/);
                    if (m) prog = m[0];
                } else if (body.includes('Compiling')) {
                    prog = 'Compiling';
                } else if (body.includes('Preparing')) {
                    prog = 'Preparing';
                }

                const runBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText && (b.innerText.includes('Latest run') || b.innerText.includes('run ·')));
                const runText = runBtn ? runBtn.innerText.trim() : '';

                const passedMatches = body.match(/(\\d+)\\s*passed/i);
                const majorMatches = body.match(/(\\d+)\\s*major/i);
                const minorMatches = body.match(/(\\d+)\\s*minor/i);

                return {
                    isRunning,
                    prog,
                    runText,
                    passed: passedMatches ? passedMatches[0] : null,
                    major: majorMatches ? majorMatches[0] : null,
                    minor: minorMatches ? minorMatches[0] : null
                };
            }""")
            elapsed = int(time.time() - start)
            print(f"[{elapsed}s] isRunning={info['isRunning']} | prog={info['prog']} | run={info['runText']} | passed={info['passed']} | major={info['major']} | minor={info['minor']}", flush=True)

            if not info['isRunning'] and cycle >= 2:
                print("AutoQC finished! Waiting 5s...", flush=True)
                await asyncio.sleep(5)
                break

    await page.screenshot(path='autoqc_expanded_run_result.png')
    print("Saved autoqc_expanded_run_result.png", flush=True)

    # Check Navigation
    nav_btn = page.locator('button[title="Navigation"]')
    if await nav_btn.count() > 0:
        await nav_btn.first.click(force=True)
        await asyncio.sleep(2)
        await page.screenshot(path='final_navigation_checklist.png')
        print("Saved final_navigation_checklist.png", flush=True)

    await p.stop()

if __name__ == '__main__':
    asyncio.run(expand_and_run())
