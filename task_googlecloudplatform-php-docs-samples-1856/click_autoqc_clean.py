import asyncio
import json
import sys
import time
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def run_qc():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    # 1. Click sidebar 'Deliverable AutoQC' tab
    tab_clicked = await page.evaluate("""() => {
        const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText && b.innerText.trim() === 'Deliverable AutoQC');
        if (btn) {
            btn.click();
            return true;
        }
        return false;
    }""")
    print("Clicked 'Deliverable AutoQC' tab:", tab_clicked, flush=True)
    await asyncio.sleep(2)

    # 2. Click 'Run AutoQC' button
    run_clicked = await page.evaluate("""() => {
        const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText && b.innerText.includes('Run AutoQC'));
        if (btn) {
            btn.click();
            return { ok: true, text: btn.innerText.trim(), disabled: btn.disabled };
        }
        return { ok: false };
    }""")
    print("Clicked 'Run AutoQC':", run_clicked, flush=True)

    # 3. Monitor until running completes
    start = time.time()
    for i in range(35):
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

            return { isRunning, prog, runText };
        }""")
        elapsed = int(time.time() - start)
        print(f"[{elapsed}s] isRunning={info['isRunning']}, prog={info['prog']}, run={info['runText']}", flush=True)

        if not info['isRunning'] and i >= 3:
            print("AutoQC finished! Waiting 5s...", flush=True)
            await asyncio.sleep(5)
            break

    # 4. Capture AutoQC text and screenshot
    qc_text = await page.evaluate("""() => {
        const t = document.body.innerText;
        const idx = t.indexOf('DELIVERABLE AUTOQC');
        return idx !== -1 ? t.substring(idx, idx + 4000) : t.substring(0, 4000);
    }""")
    print("\n=== AUTOQC RESULT ===")
    print(qc_text)

    await page.screenshot(path='autoqc_fresh_result.png')
    print("Saved autoqc_fresh_result.png", flush=True)

    # 5. Check Navigation checklist
    await page.evaluate("""() => {
        const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText && b.innerText.trim() === 'Navigation');
        if (btn) btn.click();
    }""")
    await asyncio.sleep(2)
    await page.screenshot(path='submit_navigation_checklist_fresh.png')
    print("Saved submit_navigation_checklist_fresh.png", flush=True)

    await p.stop()

if __name__ == '__main__':
    asyncio.run(run_qc())
