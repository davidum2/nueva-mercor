import asyncio
import json
import os
import sys
import time
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_f5ba2eb1464a4db2831f60a63283341d'
TASK_DIR = os.path.join(r'c:\desarrollo\nueva-mercor', f'task_{TASK_ID}')

DIM3_REASON_A = "In terms of diff cleanliness and shape, Model A's two-line configuration diff in 'build/vite/conf.js' is surgical and free of gratuitous reformatting, code duplication, dead code, or unrequested refactoring. However, substantively it fails project conventions and utility reuse by removing a required manual chunk pattern without adding the replacement package (patch_a.diff:L8-14), and by introducing an unrelated pre-existing package ('trzsz') into dependency pre-bundling exclusions (patch_a.diff:L24)."

async def run():
    p = await async_playwright().start()
    b = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [pg for pg in b.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url][0]

    print("1. Updating Task Custom Field for Dimension 3 Reason A...")
    cf_res = await page.evaluate('''async ({ dim3Ra }) => {
        const token = await window.Clerk.session.getToken({ skipCache: true });
        const headers = {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json',
            'x-campaign-id': localStorage.getItem('x-campaign-id') || 'camp_75099d23386f4394ab7596a5ea538da8',
            'x-company-id': localStorage.getItem('x-company-id') || 'comp_2fa4115109d741cd94a3c409ed89e61f',
            'x-account-id': localStorage.getItem('x-account-id') || 'acct_85b680d4c5ba49a29f19c173672aebea'
        };

        const taskId = 'task_f5ba2eb1464a4db2831f60a63283341d';
        const patchFields = {
            field_ta_dim3_reason_a: dim3Ra
        };

        const tRes = await fetch(`https://api.studio.mercor.com/tasks/${taskId}`, {
            method: 'PATCH',
            headers,
            body: JSON.stringify({ custom_fields: patchFields })
        });
        return { status: tRes.status };
    }''', {'dim3Ra': DIM3_REASON_A})
    print("Task CF patch status:", cf_res)

    await asyncio.sleep(2)

    print("\n2. Triggering AutoQC (Clicking Run AutoQC / Rerun 1 failing)...")
    click_res = await page.evaluate('''() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const rerunBtn = btns.find(b => b.innerText && b.innerText.trim() === 'Rerun 1 failing');
        if (rerunBtn) {
            rerunBtn.scrollIntoView({ behavior: 'instant', block: 'center' });
            rerunBtn.click();
            return { ok: true, text: rerunBtn.innerText };
        }
        const runBtn = btns.find(b => b.innerText && b.innerText.trim() === 'Run AutoQC');
        if (runBtn) {
            runBtn.scrollIntoView({ behavior: 'instant', block: 'center' });
            runBtn.click();
            return { ok: true, text: runBtn.innerText };
        }
        return { ok: false };
    }''')
    print("AutoQC trigger result:", click_res)

    print("\n3. Monitoring AutoQC execution...")
    start = time.time()
    for cycle in range(60):
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
            print("AutoQC execution finished! Settling 3s...")
            await asyncio.sleep(3)
            break

    # Screenshot of AutoQC pane
    ss_autoqc = os.path.join(TASK_DIR, 'autoqc_all_passed.png')
    await page.screenshot(path=ss_autoqc)
    print(f"Saved {ss_autoqc}")

    print("\n4. Checking Navigation checklist status...")
    await page.evaluate('''() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const nav = btns.find(b => b.innerText && b.innerText.trim() === 'Navigation');
        if (nav) nav.click();
    }''')
    await asyncio.sleep(2.5)

    checklist_status = await page.evaluate('''() => {
        const navHeader = Array.from(document.querySelectorAll('*')).find(el => el.innerText && el.innerText.trim() === 'Before you submit');
        if (!navHeader) return [];

        const listContainer = navHeader.parentElement;
        const listItems = Array.from(listContainer.querySelectorAll('li, div, [role="listitem"]')).filter(el => {
            const t = el.innerText || '';
            return t.includes('Length limits') || t.includes('AutoQC') || t.includes('Submit');
        });

        return listItems.map(el => {
            const svgs = Array.from(el.querySelectorAll('svg')).map(s => s.className.baseVal || s.getAttribute('class'));
            const text = el.innerText.trim().split('\\n')[0];
            const isGreen = el.innerHTML.includes('text-green') || el.innerHTML.includes('lucide-check') || el.className.includes('green') || svgs.some(c => c && (c.includes('green') || c.includes('check')));
            const isRed = el.innerHTML.includes('text-red') || el.innerHTML.includes('destructive') || svgs.some(c => c && (c.includes('red') || c.includes('alert')));
            return { text, isGreen, isRed };
        });
    }''')

    print("\n=== FINAL CHECKLIST ITEMS STATUS ===")
    all_green = True
    for it in checklist_status:
        st = "GREEN" if it.get('isGreen') else ("RED" if it.get('isRed') else "GRAY")
        if not it.get('isGreen'):
            all_green = False
        print(f"[{st}] {it.get('text')}")

    print(f"\nALL 100% GREEN: {all_green}")

    ss_nav = os.path.join(TASK_DIR, 'navigation_100_percent_all_green_verified.png')
    await page.screenshot(path=ss_nav)
    print(f"Saved {ss_nav}")

    await b.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
