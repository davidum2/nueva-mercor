import asyncio
import json
import sys
import time
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def run_and_verify_autoqc():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    # Navigate to Deliverable AutoQC tab
    autoqc_tab = page.locator('span:text-is("Deliverable AutoQC")')
    if await autoqc_tab.count() > 0:
        await autoqc_tab.first.click()
        await asyncio.sleep(2)

    # Click Run AutoQC
    run_btn = page.locator('button:has-text("Run AutoQC")')
    if await run_btn.count() > 0 and await run_btn.first.is_enabled():
        print("Clicking 'Run AutoQC'...", flush=True)
        await run_btn.first.click()
    else:
        # Check if there is a rerun button
        rerun_btn = page.locator('button:has-text("Rerun")')
        if await rerun_btn.count() > 0 and await rerun_btn.first.is_enabled():
            print("Clicking Rerun button...", flush=True)
            await rerun_btn.first.click()
        else:
            print("No Run/Rerun button available, checking running status...", flush=True)

    # Poll until AutoQC completes
    start = time.time()
    for cycle in range(60):
        await asyncio.sleep(4)
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
        print(f"[{elapsed}s] AutoQC running: {info['isRunning']} | stage: {info['stage']}", flush=True)
        if not info['isRunning'] and cycle >= 2:
            print("AutoQC execution finished!", flush=True)
            break

    # Take screenshot of AutoQC results
    await page.screenshot(path='autoqc_new_run_results.png')
    print("Saved autoqc_new_run_results.png")

    # Navigate to Navigation tab under Submit review
    nav_tab = page.locator('span:text-is("Navigation")')
    if await nav_tab.count() > 0:
        await nav_tab.first.click()
        await asyncio.sleep(2)
        await page.evaluate('''() => {
            const el = Array.from(document.querySelectorAll('*')).find(e => e.innerText && e.innerText.startsWith('Before you submit'));
            if (el) el.scrollIntoView({ behavior: 'instant', block: 'start' });
        }''')
        await asyncio.sleep(1)
        await page.screenshot(path='navigation_checklist_new_run.png')
        print("Saved navigation_checklist_new_run.png")

    # Inspect the checklist items from DOM
    checklist_status = await page.evaluate('''() => {
        const listItems = Array.from(document.querySelectorAll('li')).filter(l => {
            const t = l.innerText || '';
            return t.includes('Length limits') || t.includes('AutoQC failures') || t.includes('AutoQC up to date');
        });
        const submitBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText && b.innerText.includes('Submit for Final QC'));

        return {
            items: listItems.map(l => ({
                text: l.innerText.replace(/\\n/g, ' ').trim(),
                has_green_check: !l.innerText.includes('?') && !l.innerHTML.includes('text-red') && !l.innerHTML.includes('text-rose') && (l.innerHTML.includes('text-emerald') || l.innerHTML.includes('text-green') || l.innerHTML.includes('stroke="#10b981"') || l.innerHTML.includes('currentColor'))
            })),
            submitBtn: submitBtn ? {
                text: submitBtn.innerText,
                disabled: submitBtn.disabled
            } : null
        };
    }''')

    print("\n=== CHECKLIST STATUS ===")
    print(json.dumps(checklist_status, indent=2))

    await p.stop()

if __name__ == '__main__':
    asyncio.run(run_and_verify_autoqc())
