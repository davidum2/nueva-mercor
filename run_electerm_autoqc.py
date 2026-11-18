import asyncio
import json
import os
import sys
import time
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_f5ba2eb1464a4db2831f60a63283341d'
TASK_DIR = os.path.join(r'c:\desarrollo\nueva-mercor', f'task_{TASK_ID}')

async def run_autoqc_and_check_nav():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    # Close any overlays/menus
    await page.keyboard.press("Escape")
    await asyncio.sleep(1)

    # 1. Click Deliverable AutoQC in sidebar
    print("Clicking Deliverable AutoQC tab...", flush=True)
    await page.evaluate("""() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const tab = btns.find(b => b.innerText && b.innerText.trim() === 'Deliverable AutoQC');
        if (tab) tab.click();
    }""")
    await asyncio.sleep(2)

    # 2. Check for Run AutoQC or dropdown button
    print("Looking for Run AutoQC button...", flush=True)
    clicked = await page.evaluate("""() => {
        // Try direct Run AutoQC button
        const btns = Array.from(document.querySelectorAll('button, div'));
        const directRun = btns.find(b => b.innerText && b.innerText.trim() === 'Run AutoQC');
        if (directRun) {
            directRun.click();
            return { ok: true, type: 'direct' };
        }

        // Try dropdown Latest run · ...
        const dropdown = btns.find(b => b.innerText && (b.innerText.includes('Latest run') || b.innerText.includes('run ·')));
        if (dropdown) {
            dropdown.click();
            return { ok: true, type: 'dropdown' };
        }
        return { ok: false };
    }""")
    print("Click result:", clicked, flush=True)
    await asyncio.sleep(1.5)

    if clicked.get('type') == 'dropdown':
        # Click Run AutoQC item in dropdown
        sub_clicked = await page.evaluate("""() => {
            const all = Array.from(document.querySelectorAll('[role="menuitem"], button, div'));
            const target = all.find(el => el.innerText && el.innerText.trim() === 'Run AutoQC');
            if (target) {
                target.click();
                return true;
            }
            return false;
        }""")
        print("Clicked Run AutoQC inside dropdown:", sub_clicked, flush=True)
        await asyncio.sleep(2)

    # 3. Monitor AutoQC execution
    print("Monitoring AutoQC run...", flush=True)
    start = time.time()
    for cycle in range(40):
        await asyncio.sleep(4)
        info = await page.evaluate("""() => {
            const body = document.body.innerText;
            const isRunning = body.includes('AutoQC is running') || body.includes('Compiling') || body.includes('Running AutoQC');
            let prog = '';
            const m = body.match(/Analyzing \\d+\\/\\d+/);
            if (m) prog = m[0];
            else if (body.includes('Compiling')) prog = 'Compiling';
            else if (body.includes('Preparing')) prog = 'Preparing';

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
            print("AutoQC execution finished! Settling 5s...", flush=True)
            await asyncio.sleep(5)
            break

    # 4. Screenshot AutoQC results
    ss_autoqc = os.path.join(TASK_DIR, 'autoqc_run_result.png')
    await page.screenshot(path=ss_autoqc)
    print(f"Saved {ss_autoqc}")

    # 5. Check Navigation checklist
    print("\nNavigating to Submit review -> Navigation checklist...", flush=True)
    await page.evaluate("""() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const nav = btns.find(b => b.innerText && b.innerText.trim() === 'Navigation');
        if (nav) nav.click();
    }""")
    await asyncio.sleep(2.5)

    nav_report = await page.evaluate("""() => {
        const body = document.body.innerText;
        const navIdx = body.indexOf('NAVIGATION');
        const snippet = navIdx !== -1 ? body.substring(navIdx, navIdx + 2500) : body.substring(0, 2500);

        // Check for any red badges or incomplete items
        const items = Array.from(document.querySelectorAll('li, div')).filter(el => {
            const t = el.innerText || '';
            return t.includes('required') || t.includes('AutoQC') || t.includes('Length limits');
        }).map(el => el.innerText.trim());

        return {
            snippet,
            itemsCount: items.length
        };
    }""")

    print("\n=== NAVIGATION CHECKLIST SNIPPET ===")
    print(nav_report['snippet'])

    ss_nav = os.path.join(TASK_DIR, 'navigation_checklist_result.png')
    await page.screenshot(path=ss_nav)
    print(f"Saved {ss_nav}")

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run_autoqc_and_check_nav())
