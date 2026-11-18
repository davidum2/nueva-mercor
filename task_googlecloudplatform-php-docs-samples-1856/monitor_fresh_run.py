import asyncio
import sys
import time
import json
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def monitor():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    start_time = time.time()
    print("Starting monitoring of fresh AutoQC run...", flush=True)

    for i in range(50): # up to ~300 seconds
        await asyncio.sleep(6)
        elapsed = int(time.time() - start_time)

        status = await page.evaluate('''() => {
            const body = document.body.innerText;
            const isRunning = body.includes('AutoQC is running') || body.includes('Compiling') || body.includes('Analyzing') || body.includes('Staging context') || body.includes('Preparing');

            const passedMatches = body.match(/(\\d+)\\s*passed/i);
            const majorMatches = body.match(/(\\d+)\\s*major/i);
            const minorMatches = body.match(/(\\d+)\\s*minor/i);
            const runBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText && (b.innerText.includes('Latest run') || b.innerText.includes('run ·')));

            // Extract stages if visible
            const stageText = body.match(/(Preparing|Staging context|Analyzing \\d+\\/\\d+|Compiling)/g);

            return {
                isRunning,
                elapsedStage: stageText ? stageText.join(' -> ') : null,
                runText: runBtn ? runBtn.innerText.trim() : null,
                passed: passedMatches ? passedMatches[0] : null,
                major: majorMatches ? majorMatches[0] : null,
                minor: minorMatches ? minorMatches[0] : null
            };
        }''')

        print(f"[{elapsed}s] isRunning={status['isRunning']} | stage={status['elapsedStage']} | passed={status['passed']} | major={status['major']} | minor={status['minor']} | run={status['runText']}", flush=True)

        if not status['isRunning'] and i >= 3:
            print("AutoQC finished running! Waiting 5s to settle...", flush=True)
            await asyncio.sleep(5)
            break

    # Dump the AutoQC results
    report = await page.evaluate('''() => {
        const body = document.body.innerText;
        const autoqcCard = Array.from(document.querySelectorAll('*'))
            .filter(el => el.innerText && el.innerText.includes('DELIVERABLE AUTOQC') && el.innerText.includes('check your work'))[0];
        
        const cardText = autoqcCard ? autoqcCard.innerText : body.slice(0, 3000);

        const testItems = [];
        document.querySelectorAll('div, li').forEach(d => {
            const t = d.innerText || '';
            if (t.includes('Passed') || t.includes('passed') || t.includes('Major') || t.includes('Minor') || t.includes('Every Rubric')) {
                if (t.length < 300 && !t.includes('\\n\\n\\n')) {
                    testItems.push(t.trim());
                }
            }
        });

        return {
            cardText,
            testItems: Array.from(new Set(testItems)).slice(0, 40)
        };
    }''')

    print("\n=== FINAL AUTOQC OUTPUT ===")
    print(report['cardText'])
    print("===========================\n")

    await page.screenshot(path='fresh_run_autoqc_result.png')
    print("Saved fresh_run_autoqc_result.png")

    # Navigate to Submit review -> Navigation
    nav_item = page.locator('span:text-is("Navigation")')
    if await nav_item.count() > 0:
        await nav_item.first.click()
        await asyncio.sleep(2)
        # Scroll to checklist
        await page.evaluate('''() => {
            const el = Array.from(document.querySelectorAll('*')).find(e => e.innerText && e.innerText.startsWith('Before you submit'));
            if (el) el.scrollIntoView({ behavior: 'instant', block: 'start' });
        }''')
        await asyncio.sleep(1)
        await page.screenshot(path='fresh_run_submit_checklist.png')
        print("Saved fresh_run_submit_checklist.png")

    # Extract all checklist rows
    checklist = await page.evaluate('''() => {
        return Array.from(document.querySelectorAll('div, li'))
            .filter(el => el.innerText && (el.innerText.includes('Length limits') || el.innerText.includes('AutoQC failures') || el.innerText.includes('AutoQC up to date')))
            .map(el => el.innerText.split('\\n')[0]);
    }''')
    print("Checklist rows:", list(set(checklist)))

    await p.stop()
    print("Monitoring script completed successfully!", flush=True)

asyncio.run(monitor())
