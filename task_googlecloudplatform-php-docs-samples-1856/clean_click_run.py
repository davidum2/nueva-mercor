import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def clean_click_run():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]
    
    # Press Escape to close any open dropdown
    await page.keyboard.press("Escape")
    await asyncio.sleep(1)
    
    # Click Run AutoQC via JS evaluate to bypass poppers
    res = await page.evaluate("""() => {
        const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText && b.innerText.includes('Run AutoQC'));
        if (btn) {
            btn.click();
            return { ok: true, text: btn.innerText.trim() };
        }
        return { ok: false };
    }""")
    print("Click result:", res, flush=True)
    await asyncio.sleep(4)
    
    is_running = await page.evaluate("() => document.body.innerText.includes('AutoQC is running')")
    print(f"AutoQC is running: {is_running}", flush=True)
    
    await page.screenshot(path='autoqc_rerun_clean.png')
    print("Saved autoqc_rerun_clean.png", flush=True)
    await p.stop()

if __name__ == '__main__':
    asyncio.run(clean_click_run())
