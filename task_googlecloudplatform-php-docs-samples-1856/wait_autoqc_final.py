import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def wait_completion():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]
    
    print("Waiting for AutoQC to finish running...", flush=True)
    for i in range(25): # up to ~120s
        is_running = await page.evaluate("() => document.body.innerText.includes('AutoQC is running')")
        print(f"[{i+1}] AutoQC running: {is_running}", flush=True)
        if not is_running:
            print("AutoQC completed!", flush=True)
            break
        await asyncio.sleep(5)
        
    await asyncio.sleep(2)
    await page.screenshot(path='autoqc_final_outcome.png')
    print("Saved autoqc_final_outcome.png", flush=True)

    # Extract all text from AutoQC section
    summary = await page.evaluate("""() => {
        const buttons = Array.from(document.querySelectorAll('button')).map(b => b.innerText.trim());
        const filters = buttons.filter(b => b.includes('issues') || b.includes('Passed') || b === 'All');
        return {
            filters,
            bodySnippet: document.body.innerText.slice(0, 1200)
        };
    }""")
    print("Filters:", summary['filters'], flush=True)

    await p.stop()

if __name__ == '__main__':
    asyncio.run(wait_completion())
