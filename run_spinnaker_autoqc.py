import asyncio
import os
import sys
import time
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_08ccf272669347c3af63de71b2ecb5e5'
TASK_DIR = os.path.join(r'c:\desarrollo\nueva-mercor', f'task_task_{TASK_ID}')

async def run_autoqc():
    p = await async_playwright().start()
    b = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [pg for pg in b.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url][0]

    # Open Deliverable AutoQC accordion / tab
    print("1. Opening Deliverable AutoQC...")
    await page.evaluate('''() => {
        const btns = Array.from(document.querySelectorAll('button, div, span, h2, h3, h4'));
        const tab = btns.find(b => {
            const t = (b.innerText || '').trim();
            return t === 'Deliverable AutoQC' || t.startsWith('DELIVERABLE AUTOQC');
        });
        if (tab) tab.click();
    }''')
    await asyncio.sleep(2)

    # Find Run AutoQC button
    print("2. Finding and clicking Run AutoQC...")
    click_res = await page.evaluate('''() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const directRun = btns.find(b => b.innerText && b.innerText.trim() === 'Run AutoQC');
        if (directRun) {
            directRun.scrollIntoView({ behavior: 'instant', block: 'center' });
            directRun.click();
            return { ok: true, type: 'direct', text: directRun.innerText };
        }

        const dropdown = btns.find(b => b.innerText && (b.innerText.includes('Latest run') || b.innerText.includes('run ·')));
        if (dropdown) {
            dropdown.scrollIntoView({ behavior: 'instant', block: 'center' });
            dropdown.click();
            return { ok: true, type: 'dropdown', text: dropdown.innerText };
        }

        // Also check if there is a 'Rerun' button
        const rerun = btns.find(b => b.innerText && b.innerText.includes('Rerun'));
        if (rerun) {
            rerun.scrollIntoView({ behavior: 'instant', block: 'center' });
            rerun.click();
            return { ok: true, type: 'rerun', text: rerun.innerText };
        }

        return { ok: false };
    }''')
    print("Click result:", click_res)

    if click_res.get('type') == 'dropdown':
        await asyncio.sleep(1)
        sub_res = await page.evaluate('''() => {
            const all = Array.from(document.querySelectorAll('[role="menuitem"], button, div, span'));
            const target = all.find(el => el.innerText && el.innerText.trim() === 'Run AutoQC');
            if (target) {
                target.click();
                return { ok: true, text: target.innerText };
            }
            return { ok: false };
        }''')
        print("Sub-menu Run AutoQC result:", sub_res)

    await asyncio.sleep(2)

    print("\n3. Monitoring AutoQC execution...")
    start = time.time()
    for cycle in range(75):
        await asyncio.sleep(4)
        info = await page.evaluate('''() => {
            const body = document.body.innerText;
            const isRunning = body.includes('AutoQC is running') || body.includes('Compiling') || body.includes('Running AutoQC') || body.includes('Analyzing');
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
        }''')
        elapsed = int(time.time() - start)
        print(f"[{elapsed}s] isRunning={info['isRunning']} | prog={info['prog']} | run={info['runText']} | passed={info['passed']} | major={info['major']} | minor={info['minor']}", flush=True)

        if not info['isRunning'] and cycle >= 4:
            print("AutoQC finished running! Settling 3s...")
            await asyncio.sleep(3)
            break

    # Save AutoQC screenshot
    ss_autoqc = os.path.join(TASK_DIR, 'autoqc_post_run_spinnaker.png')
    await page.screenshot(path=ss_autoqc)
    print(f"Saved {ss_autoqc}")

    # Check AutoQC failures if any
    failures = await page.evaluate('''() => {
        const body = document.body.innerText;
        const out = [];
        // Look for cards with red badges or failure descriptions
        const cards = Array.from(document.querySelectorAll('div, li')).filter(el => {
            const t = el.innerText || '';
            return t.includes('FAIL') || t.includes('major') || t.includes('minor');
        });
        return cards.slice(0, 10).map(c => c.innerText.substring(0, 150));
    }''')
    print("Failure candidates:", failures[:5])

    # Switch back to Navigation checklist
    print("\n4. Checking Navigation checklist...")
    await page.evaluate('''() => {
        const btns = Array.from(document.querySelectorAll('button, div, span'));
        const nav = btns.find(b => b.innerText && b.innerText.trim() === 'Navigation');
        if (nav) nav.click();
    }''')
    await asyncio.sleep(2)

    items = await page.evaluate('''() => {
        const navHeader = Array.from(document.querySelectorAll('*')).find(el => el.innerText && el.innerText.trim() === 'Before you submit');
        if (!navHeader) return [];

        const listContainer = navHeader.parentElement;
        const listItems = Array.from(listContainer.querySelectorAll('li, div, [role="listitem"]')).filter(el => {
            const t = el.innerText || '';
            return t.includes('Dimension') || t.includes('Rubric') || t.includes('Task type') || t.includes('Pairwise') || t.includes('Comparative') || t.includes('Length') || t.includes('AutoQC') || t.includes('score') || t.includes('reason') || t.includes('answer');
        });

        return listItems.map(el => {
            const svgs = Array.from(el.querySelectorAll('svg')).map(s => s.className.baseVal || s.getAttribute('class'));
            const text = el.innerText.trim().split('\\n')[0];
            const isGreen = el.innerHTML.includes('text-green') || el.innerHTML.includes('lucide-check') || el.className.includes('green') || svgs.some(c => c && (c.includes('green') || c.includes('check')));
            const isRed = el.innerHTML.includes('text-red') || el.innerHTML.includes('destructive') || svgs.some(c => c && (c.includes('red') || c.includes('alert')));
            return { text, isGreen, isRed };
        });
    }''')

    print(f"\n=== FINAL CHECKLIST ({len(items)} items) ===")
    for it in items:
        st = "GREEN" if it.get('isGreen') else ("RED" if it.get('isRed') else "GRAY")
        print(f"[{st}] {it.get('text')}")

    ss_final = os.path.join(TASK_DIR, 'final_navigation_checklist_success.png')
    await page.screenshot(path=ss_final)
    print(f"Saved {ss_final}")

    await b.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run_autoqc())
