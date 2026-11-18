import asyncio
import json
import sys
import time
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def trigger_autoqc_dropdown():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    # 1. Click Deliverable AutoQC tab
    await page.evaluate("""() => {
        const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText && b.innerText.trim() === 'Deliverable AutoQC');
        if (btn) btn.click();
    }""")
    await asyncio.sleep(2)

    # 2. Click the Latest run dropdown button
    dropdown_clicked = await page.evaluate("""() => {
        const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText && (b.innerText.includes('Latest run') || b.innerText.includes('run ·')));
        if (btn) {
            btn.click();
            return { ok: true, text: btn.innerText.trim() };
        }
        return { ok: false };
    }""")
    print("Clicked run dropdown:", dropdown_clicked, flush=True)
    await asyncio.sleep(1)

    # 3. Check menu items in dropdown
    menu_items = await page.evaluate("""() => {
        return Array.from(document.querySelectorAll('[role="menuitem"], [role="option"], div, button'))
            .map(el => el.innerText ? el.innerText.trim() : '')
            .filter(t => t.includes('Run') || t.includes('AutoQC') || t.includes('run'));
    }""")
    print("Found potential menu items in dropdown:")
    for item in set(menu_items[:15]):
        print("  ->", repr(item))

    # 4. Click 'Run AutoQC' inside the dropdown/page
    clicked_run = await page.evaluate("""() => {
        // Look for menu item or button that says 'Run AutoQC'
        const all = Array.from(document.querySelectorAll('[role="menuitem"], button, div'));
        const target = all.find(el => el.innerText && el.innerText.trim() === 'Run AutoQC');
        if (target) {
            target.click();
            return { ok: true, tag: target.tagName, text: target.innerText.trim() };
        }
        return { ok: false };
    }""")
    print("Clicked Run AutoQC target:", clicked_run, flush=True)
    await asyncio.sleep(2)

    await page.screenshot(path='autoqc_rerun_started.png')
    print("Saved autoqc_rerun_started.png", flush=True)

    # 5. Monitor AutoQC progress
    print("Monitoring AutoQC run...", flush=True)
    start = time.time()
    for cycle in range(35):
        await asyncio.sleep(4)
        status = await page.evaluate("""() => {
            const body = document.body.innerText;
            const isRunning = body.includes('AutoQC is running') || body.includes('Running AutoQC');
            let prog = '';
            const m = body.match(/Analyzing \\d+\\/\\d+/);
            if (m) prog = m[0];
            else if (body.includes('Compiling')) prog = 'Compiling';
            else if (body.includes('Preparing')) prog = 'Preparing';

            const runBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText && (b.innerText.includes('Latest run') || b.innerText.includes('run ·')));
            const runText = runBtn ? runBtn.innerText.trim() : '';

            return { isRunning, prog, runText };
        }""")
        elapsed = int(time.time() - start)
        print(f"[{elapsed}s] isRunning={status['isRunning']} | prog={status['prog']} | {status['runText']}", flush=True)

        if not status['isRunning'] and cycle >= 3:
            print("AutoQC completed!", flush=True)
            await asyncio.sleep(4)
            break

    # 6. Capture full AutoQC status
    qc_summary = await page.evaluate("""() => {
        const body = document.body.innerText;
        const passedMatch = body.match(/(\\d+)\\s*passed/i);
        const majorMatch = body.match(/(\\d+)\\s*major/i);
        const minorMatch = body.match(/(\\d+)\\s*minor/i);
        return {
            passed: passedMatch ? passedMatch[0] : null,
            major: majorMatch ? majorMatch[0] : null,
            minor: minorMatch ? minorMatch[0] : null
        };
    }""")
    print("\n=== AUTOQC SUMMARY ===")
    print(json.dumps(qc_summary, indent=2))

    await page.screenshot(path='autoqc_latest_results.png')
    print("Saved autoqc_latest_results.png", flush=True)

    # 7. Check Submit review -> Navigation checklist
    print("\nChecking Navigation checklist...", flush=True)
    await page.evaluate("""() => {
        const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText && b.innerText.trim() === 'Navigation');
        if (btn) btn.click();
    }""")
    await asyncio.sleep(2)
    await page.screenshot(path='final_navigation_checklist_latest.png')
    print("Saved final_navigation_checklist_latest.png", flush=True)

    await p.stop()

if __name__ == '__main__':
    asyncio.run(trigger_autoqc_dropdown())
