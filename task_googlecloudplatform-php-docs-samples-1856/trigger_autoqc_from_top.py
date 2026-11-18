import asyncio
import json
import sys
import time
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def trigger():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    # Scroll all scrollable elements to top
    await page.evaluate("""() => {
        window.scrollTo(0, 0);
        document.querySelectorAll('*').forEach(el => {
            if (el.scrollTop > 0) el.scrollTop = 0;
        });
    }""")
    await asyncio.sleep(1)

    # Click DELIVERABLE AUTOQC header to expand
    expand_res = await page.evaluate("""() => {
        const div = Array.from(document.querySelectorAll('div')).find(d => {
            return d.className.includes('cursor-pointer') && d.innerText && d.innerText.trim().startsWith('DELIVERABLE AUTOQC');
        });
        if (div) {
            div.scrollIntoView();
            div.click();
            return { ok: true, text: div.innerText.trim() };
        }
        return { ok: false };
    }""")
    print("Expand result:", expand_res, flush=True)
    await asyncio.sleep(2)

    # Click Run AutoQC
    click_res = await page.evaluate("""() => {
        const btn = Array.from(document.querySelectorAll('button')).find(b => {
            return b.innerText && b.innerText.includes('Run AutoQC');
        });
        if (btn) {
            btn.scrollIntoView();
            btn.click();
            return { ok: true, text: btn.innerText.trim() };
        }
        return { ok: false };
    }""")
    print("Click Run AutoQC result:", click_res, flush=True)

    if not click_res['ok']:
        print("Run AutoQC button not found, screenshotting...", flush=True)
        await page.screenshot(path='debug_not_found.png')
        await p.stop()
        return

    # Monitor run
    print("Monitoring AutoQC run...", flush=True)
    start = time.time()
    for cycle in range(45):
        await asyncio.sleep(4)
        info = await page.evaluate("""() => {
            const body = document.body.innerText;
            const isRunning = body.includes('AutoQC is running') || body.includes('Compiling');
            
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
            print("AutoQC execution finished! Settling 5s...", flush=True)
            await asyncio.sleep(5)
            break

    # Dump full AutoQC content
    report = await page.evaluate("""() => {
        const body = document.body.innerText;
        const autoqcIdx = body.indexOf('DELIVERABLE AUTOQC');
        const snippet = autoqcIdx !== -1 ? body.substring(autoqcIdx, autoqcIdx + 4000) : body.substring(0, 4000);

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

    print("\n=== AUTOQC FINAL RUN REPORT ===")
    print(report['snippet'])
    print(f"\nTotal issue cards: {len(report['issueCards'])}")
    for c in report['issueCards']:
        print("CARD:", c)

    await page.screenshot(path='autoqc_fresh_passed_result.png')
    print("Saved autoqc_fresh_passed_result.png", flush=True)

    # Check Submit Review -> Navigation
    nav_btn = page.locator('button[title="Navigation"]')
    if await nav_btn.count() > 0:
        await nav_btn.first.click(force=True)
        await asyncio.sleep(2)
        await page.screenshot(path='final_navigation_checklist_fresh.png')
        print("Saved final_navigation_checklist_fresh.png", flush=True)

    await p.stop()
    print("Complete!", flush=True)

if __name__ == '__main__':
    asyncio.run(trigger())
