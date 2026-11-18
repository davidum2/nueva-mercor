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

    # Expand DELIVERABLE AUTOQC accordion
    expanded = await page.evaluate("""() => {
        // Find accordion trigger with DELIVERABLE AUTOQC
        const headers = Array.from(document.querySelectorAll('button, div, h3')).filter(el => {
            return el.innerText && el.innerText.trim().startsWith('DELIVERABLE AUTOQC');
        });
        for (const h of headers) {
            // Check if it has an aria-expanded attribute or is a button
            if (h.getAttribute('aria-expanded') === 'false' || h.tagName === 'BUTTON') {
                h.click();
                return { clicked: true, tag: h.tagName, text: h.innerText.trim() };
            }
        }
        return { clicked: false, count: headers.length };
    }""")
    print("Accordion expand result:", json.dumps(expanded), flush=True)
    await asyncio.sleep(2)

    # Click Run AutoQC
    run_res = await page.evaluate("""() => {
        const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText && b.innerText.includes('Run AutoQC'));
        if (btn) {
            btn.click();
            return { ok: true, text: btn.innerText.trim() };
        }
        return { ok: false, buttons: Array.from(document.querySelectorAll('button')).map(b => b.innerText.trim()).filter(Boolean) };
    }""")
    print("Run AutoQC click result:", json.dumps(run_res, indent=2), flush=True)

    if not run_res['ok']:
        print("Run AutoQC button still not found. Taking debug screenshot...", flush=True)
        await page.screenshot(path='autoqc_debug_accordion.png')
        await p.stop()
        return

    # Monitor run until completed
    print("AutoQC triggered! Monitoring execution...", flush=True)
    start = time.time()
    for cycle in range(40): # up to 160s
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
            print("AutoQC finished! Waiting 5s for final UI update...", flush=True)
            await asyncio.sleep(5)
            break

    # Dump full AutoQC text
    autoqc_text = await page.evaluate("""() => {
        const t = document.body.innerText;
        const idx = t.indexOf('DELIVERABLE AUTOQC');
        return idx !== -1 ? t.substring(idx, idx + 4000) : t.substring(0, 4000);
    }""")
    print("\n=== AUTOQC FINAL RUN REPORT ===")
    print(autoqc_text)

    await page.screenshot(path='autoqc_final_passed_run.png')
    print("Saved autoqc_final_passed_run.png", flush=True)

    # Check Submit Review -> Navigation
    await page.evaluate("""() => {
        const nav = Array.from(document.querySelectorAll('button')).find(b => b.innerText && b.innerText.trim() === 'Navigation');
        if (nav) nav.click();
    }""")
    await asyncio.sleep(2)
    await page.screenshot(path='submit_checklist_final_run.png')
    print("Saved submit_checklist_final_run.png", flush=True)

    await p.stop()

if __name__ == '__main__':
    asyncio.run(expand_and_run())
