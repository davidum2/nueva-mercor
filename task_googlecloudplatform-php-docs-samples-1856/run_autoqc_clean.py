import asyncio
import json
import sys
import time
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def run_and_monitor():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    # Reload page or make sure DOM is fresh
    print("Reloading task page to ensure fresh React state...", flush=True)
    await page.reload()
    await page.wait_for_load_state("networkidle")
    await asyncio.sleep(4)

    # Click Run AutoQC via JS
    click_res = await page.evaluate("""() => {
        const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText && b.innerText.includes('Run AutoQC'));
        if (btn) {
            btn.click();
            return { ok: true, text: btn.innerText.trim(), disabled: btn.disabled };
        }
        return { ok: false };
    }""")
    print("Run AutoQC button click result:", click_res, flush=True)

    # Monitor run until completed
    start_time = time.time()
    for cycle in range(35): # ~140 seconds
        await asyncio.sleep(4)
        info = await page.evaluate("""() => {
            const text = document.body.innerText;
            const isRunning = text.includes('AutoQC is running') || text.includes('Running AutoQC...');
            
            let progress = '';
            if (text.includes('Analyzing')) {
                const match = text.match(/Analyzing \\d+\\/\\d+/);
                if (match) progress = match[0];
            } else if (text.includes('Compiling')) {
                progress = 'Compiling';
            } else if (text.includes('Preparing')) {
                progress = 'Preparing';
            }

            const runBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText && (b.innerText.includes('Latest run') || b.innerText.includes('run ·')));
            const latestRun = runBtn ? runBtn.innerText.trim() : '';

            return { isRunning, progress, latestRun };
        }""")

        elapsed = int(time.time() - start_time)
        print(f"[{elapsed}s] isRunning={info['isRunning']} | progress={info['progress']} | run={info['latestRun']}", flush=True)

        if not info['isRunning'] and cycle >= 2:
            print("AutoQC execution finished! Waiting 4 seconds for UI...", flush=True)
            await asyncio.sleep(4)
            break

    # Click Deliverable AutoQC tab if not active
    await page.evaluate("""() => {
        const tab = Array.from(document.querySelectorAll('button')).find(b => b.innerText && b.innerText.includes('Deliverable AutoQC'));
        if (tab) tab.click();
    }""")
    await asyncio.sleep(2)

    # Extract all text and results from Deliverable AutoQC
    summary = await page.evaluate("""() => {
        const allText = document.body.innerText;
        const autoqcIdx = allText.indexOf('DELIVERABLE AUTOQC');
        return autoqcIdx !== -1 ? allText.substring(autoqcIdx, autoqcIdx + 3500) : allText.substring(0, 3500);
    }""")

    print("\n=== AUTOQC FINAL SUMMARY ===")
    print(summary)

    await page.screenshot(path='autoqc_100_percent_pass.png')
    print("Saved autoqc_100_percent_pass.png", flush=True)

    # Check Submit Review -> Navigation
    await page.evaluate("""() => {
        const nav = Array.from(document.querySelectorAll('button')).find(b => b.innerText && b.innerText.trim() === 'Navigation');
        if (nav) nav.click();
    }""")
    await asyncio.sleep(2)
    await page.screenshot(path='submit_navigation_final.png')
    print("Saved submit_navigation_final.png", flush=True)

    await p.stop()

if __name__ == '__main__':
    asyncio.run(run_and_monitor())
