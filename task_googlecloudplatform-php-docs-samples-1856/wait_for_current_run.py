import asyncio
import json
import sys
import time
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def wait_run():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    # Click Deliverable AutoQC sidebar button
    autoqc_btn = page.locator('button[title="Deliverable AutoQC"]')
    if await autoqc_btn.count() > 0:
        await autoqc_btn.first.click(force=True)
        await asyncio.sleep(1)

    # If DELIVERABLE AUTOQC accordion is collapsed, click to expand
    header = page.locator('div.cursor-pointer:has-text("DELIVERABLE AUTOQC")')
    if await header.count() > 0:
        # Check if chevron is > (collapsed)
        txt = await header.first.inner_text()
        print("Header text:", txt)
        # Click to ensure expanded
        await header.first.click()
        await asyncio.sleep(1)

    print("Checking AutoQC run status...", flush=True)
    for c in range(30):
        info = await page.evaluate("""() => {
            const body = document.body.innerText;
            const isRunning = body.includes('AutoQC is running') || body.includes('Running AutoQC...');
            
            let prog = '';
            if (body.includes('Analyzing')) {
                const m = body.match(/Analyzing \\d+\\/\\d+/);
                if (m) prog = m[0];
            } else if (body.includes('Compiling')) {
                prog = 'Compiling';
            }

            const runBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText && (b.innerText.includes('Latest run') || b.innerText.includes('run ·')));
            const runText = runBtn ? runBtn.innerText.trim() : '';

            return { isRunning, prog, runText };
        }""")
        print(f"Cycle {c+1}: isRunning={info['isRunning']} | prog={info['prog']} | run={info['runText']}", flush=True)

        if not info['isRunning']:
            print("AutoQC run completed! Settling 3s...", flush=True)
            await asyncio.sleep(3)
            break
        await asyncio.sleep(5)

    # Get results text
    report = await page.evaluate("""() => {
        const body = document.body.innerText;
        const autoqcIdx = body.indexOf('DELIVERABLE AUTOQC');
        const snippet = autoqcIdx !== -1 ? body.substring(autoqcIdx, autoqcIdx + 4500) : body.substring(0, 4500);

        // Check for major / minor issue elements
        const issues = [];
        document.querySelectorAll('div').forEach(d => {
            const t = d.innerText || '';
            if (t.includes('Finding #') && (t.includes('MINOR') || t.includes('MAJOR'))) {
                if (t.length < 400) issues.push(t);
            }
        });

        return {
            snippet,
            issues: Array.from(new Set(issues))
        };
    }""")

    print("\n=== AUTOQC RESULTS DUMP ===")
    print(report['snippet'])
    print("\n=== ISSUES DETECTED ===")
    print(f"Total issue cards: {len(report['issues'])}")
    for iss in report['issues']:
        print("ISSUE:", iss)

    await page.screenshot(path='autoqc_completed_inspection.png')
    print("Saved autoqc_completed_inspection.png", flush=True)

    # Switch to Navigation
    nav_btn = page.locator('button[title="Navigation"]')
    if await nav_btn.count() > 0:
        await nav_btn.first.click(force=True)
        await asyncio.sleep(2)
        await page.screenshot(path='navigation_checklist_inspected.png')
        print("Saved navigation_checklist_inspected.png", flush=True)

    await p.stop()

if __name__ == '__main__':
    asyncio.run(wait_run())
