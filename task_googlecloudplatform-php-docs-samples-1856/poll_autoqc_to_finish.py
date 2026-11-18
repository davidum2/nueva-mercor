import asyncio
import json
import sys
import time
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def poll_until_done():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url][0]

    start = time.time()
    for cycle in range(60): # up to 5 minutes
        await asyncio.sleep(5)
        info = await page.evaluate('''() => {
            const text = document.body.innerText;
            const isRunning = text.includes('AutoQC is running');
            let stage = 'unknown';
            if (text.includes('Analyzing')) {
                const m = text.match(/Analyzing \\d+\\/\\d+/);
                stage = m ? m[0] : 'Analyzing';
            } else if (text.includes('Compiling')) {
                stage = 'Compiling';
            } else if (text.includes('Staging')) {
                stage = 'Staging';
            } else if (text.includes('Preparing')) {
                stage = 'Preparing';
            }
            return { isRunning, stage };
        }''')
        elapsed = int(time.time() - start)
        print(f"[{elapsed}s] isRunning: {info['isRunning']} | stage: {info['stage']}", flush=True)

        if not info['isRunning']:
            print("AutoQC execution finished!", flush=True)
            break

    await page.screenshot(path='autoqc_completed_run.png')
    print("Saved autoqc_completed_run.png", flush=True)
    await p.stop()

if __name__ == '__main__':
    asyncio.run(poll_until_done())
