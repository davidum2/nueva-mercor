import asyncio
import json
import sys
import time
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def wait_compiling():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    print("Polling until Compiling finishes...", flush=True)
    start = time.time()
    for cycle in range(30): # up to 150 seconds
        await asyncio.sleep(5)
        status = await page.evaluate("""() => {
            const body = document.body.innerText;
            const isRunning = body.includes('AutoQC is running') || body.includes('Compiling');
            
            // Check run time dropdown
            const runBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText && (b.innerText.includes('Latest run') || b.innerText.includes('run ·')));
            const runText = runBtn ? runBtn.innerText.trim() : '';

            // Check counts
            const passed = body.match(/(\\d+)\\s*passed/i);
            const major = body.match(/(\\d+)\\s*major/i);
            const minor = body.match(/(\\d+)\\s*minor/i);

            return {
                isRunning,
                runText,
                passed: passed ? passed[0] : null,
                major: major ? major[0] : null,
                minor: minor ? minor[0] : null
            };
        }""")
        elapsed = int(time.time() - start)
        print(f"[{elapsed}s] isRunning={status['isRunning']} | run={status['runText']} | passed={status['passed']} | major={status['major']} | minor={status['minor']}", flush=True)

        if not status['isRunning']:
            print("AutoQC Compilation complete! Waiting 4s for DOM...", flush=True)
            await asyncio.sleep(4)
            break

    # Dump full AutoQC content
    report = await page.evaluate("""() => {
        const body = document.body.innerText;
        const autoqcIdx = body.indexOf('DELIVERABLE AUTOQC');
        const snippet = autoqcIdx !== -1 ? body.substring(autoqcIdx, autoqcIdx + 3000) : body.substring(0, 3000);

        // Find all cards
        const issueCards = [];
        document.querySelectorAll('div').forEach(d => {
            const t = d.innerText || '';
            if ((t.includes('Finding #') || t.includes('issue') || t.includes('passed')) && t.length < 500) {
                issueCards.push(t);
            }
        });

        return {
            snippet,
            issueCards: Array.from(new Set(issueCards))
        };
    }""")

    print("\n=== FINAL COMPILED AUTOQC RESULTS ===")
    print(report['snippet'])
    print("\nIssue cards found:", len(report['issueCards']))

    await page.screenshot(path='autoqc_compilation_finished.png')
    print("Saved autoqc_compilation_finished.png", flush=True)

    # Check Submit Review -> Navigation checklist
    nav_btn = page.locator('button[title="Navigation"]')
    if await nav_btn.count() > 0:
        await nav_btn.first.click(force=True)
        await asyncio.sleep(2)
        await page.screenshot(path='submit_checklist_after_compilation.png')
        print("Saved submit_checklist_after_compilation.png", flush=True)

    await p.stop()

if __name__ == '__main__':
    asyncio.run(wait_compiling())
