import asyncio
import json
import os
import sys
import time
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_f5ba2eb1464a4db2831f60a63283341d'
TASK_DIR = os.path.join(r'c:\desarrollo\nueva-mercor', f'task_{TASK_ID}')

V_IDS = [
    'ver_dd7eb37982be4f3caa82c8543a8949fd', # 1
    'ver_b7b0e8fb52064a89a27e60b65beeae09', # 2
    'ver_c76f1fbf2c5148fabf34476f5b3a2a10', # 3
    'ver_f9a2f1ee086545d3a9609b4218ba3c2a', # 4
    'ver_7da28f5773d846fb868d60edbcdefab2', # 5
    'ver_b74a7d9ac65743a5af1fb52c6c0c667a', # 6
    'ver_681bd292e2c34bc0b0a614e27624e2c2', # 7
    'ver_3a17e115fde549b4bcdbd1c1667e5f82', # 8
    'ver_bcefe50ff3b2491d909aed58c47c9b6a', # 9
    'ver_e0841d99d0b24df4a8abd73fece7e4c9'  # 10
]

R1_RB = "Model B updates the 'manualChunks' function in 'build/vite/conf.js' to return 'zmodem-wasm' (patch_b.diff:L10-12), which fails to configure the required 'zmodem2-wasm' package."
R2_RB = "Model B adds 'zmodem-wasm' to 'optimizeDeps.exclude' on patch_b.diff:L21, failing to exclude the required 'zmodem2-wasm' package."
DIM7_RA = "Model A executes no post-edit verification commands, test runners, or build scripts after modifying 'build/vite/conf.js', completely skipping verification. No test weakening was committed; no test files were deleted, disabled, weakened, or modified."

async def run():
    p = await async_playwright().start()
    b = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [pg for pg in b.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url][0]

    print("1. Updating Verifiers 1 and 2 to B=NO with exact reasons...")
    v_res = await page.evaluate('''async ({ vIds, r1Rb, r2Rb }) => {
        const token = await window.Clerk.session.getToken({ skipCache: true });
        const headers = {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json',
            'x-campaign-id': localStorage.getItem('x-campaign-id') || 'camp_75099d23386f4394ab7596a5ea538da8',
            'x-company-id': localStorage.getItem('x-company-id') || 'comp_2fa4115109d741cd94a3c409ed89e61f',
            'x-account-id': localStorage.getItem('x-account-id') || 'acct_85b680d4c5ba49a29f19c173672aebea'
        };

        const res1 = await fetch(`https://api.studio.mercor.com/verifiers/${vIds[0]}`, {
            method: 'PATCH',
            headers,
            body: JSON.stringify({
                verifier_custom_field_values: {
                    answer_b: 'NO',
                    reason_b: r1Rb
                }
            })
        });

        const res2 = await fetch(`https://api.studio.mercor.com/verifiers/${vIds[1]}`, {
            method: 'PATCH',
            headers,
            body: JSON.stringify({
                verifier_custom_field_values: {
                    answer_b: 'NO',
                    reason_b: r2Rb
                }
            })
        });

        return { v1: res1.status, v2: res2.status };
    }''', {'vIds': V_IDS, 'r1Rb': R1_RB, 'r2Rb': R2_RB})
    print("Verifiers patch statuses:", v_res)

    print("\n2. Updating Task Custom Fields (Rubrics 1 & 2 answers/reasons and Dim 7 reason A)...")
    cf_res = await page.evaluate('''async ({ r1Rb, r2Rb, dim7Ra }) => {
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
            field_ta_rubric_01_answer_b: 'NO',
            field_ta_rubric_01_reason_b: r1Rb,
            field_ta_rubric_02_answer_b: 'NO',
            field_ta_rubric_02_reason_b: r2Rb,
            field_ta_dim7_reason_a: dim7Ra
        };

        const tRes = await fetch(`https://api.studio.mercor.com/tasks/${taskId}`, {
            method: 'PATCH',
            headers,
            body: JSON.stringify({ custom_fields: patchFields })
        });
        return { status: tRes.status };
    }''', {'r1Rb': R1_RB, 'r2Rb': R2_RB, 'dim7Ra': DIM7_RA})
    print("Task CF patch status:", cf_res)

    await asyncio.sleep(2)

    print("\n3. Triggering AutoQC (Clicking Run AutoQC)...")
    click_res = await page.evaluate('''() => {
        const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText && (b.innerText.trim() === 'Run AutoQC' || b.innerText.trim() === 'Rerun 2 failing'));
        if (btn) {
            btn.scrollIntoView({ behavior: 'instant', block: 'center' });
            btn.click();
            return { ok: true, text: btn.innerText };
        }
        return { ok: false };
    }''')
    print("AutoQC trigger result:", click_res)

    print("\n4. Monitoring AutoQC execution...")
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

    print("\n5. Checking Navigation checklist status...")
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

    ss_nav = os.path.join(TASK_DIR, 'navigation_100_percent_final.png')
    await page.screenshot(path=ss_nav)
    print(f"Saved {ss_nav}")

    await b.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
