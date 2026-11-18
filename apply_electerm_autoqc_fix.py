import asyncio
import json
import os
import sys
import time
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_f5ba2eb1464a4db2831f60a63283341d'
TASK_DIR = os.path.join(r'c:\desarrollo\nueva-mercor', f'task_{TASK_ID}')

RUBRIC_DATA = [
    # 01
    {
        "crit": "Does the 'manualChunks' function in 'build/vite/conf.js' maintain a dedicated return statement for ZMODEM rather than removing chunk separation entirely?",
        "ans_a": "NO", "ans_b": "YES",
        "dim": "2 · Architecture, Modularity & Trade-off Soundness",
        "src": "INFERRABLE_FROM_ENVIRONMENT",
        "ra": "Model A removes the 'zmodem-ts' chunk block in 'build/vite/conf.js' (patch_a.diff:L8-14) without providing any replacement return statement for ZMODEM, which causes all ZMODEM modules to fall into default vendor chunks.",
        "rb": "Model B retains a dedicated return statement for ZMODEM in 'manualChunks' at patch_b.diff:L10-12 ('if (id.includes(\"zmodem-wasm\")) return \"zmodem-wasm\"'), preserving independent bundle chunking for the file-transfer module."
    },
    # 02
    {
        "crit": "Does the bundler configuration target a ZMODEM package in 'optimizeDeps.exclude' rather than an unrelated tool?",
        "ans_a": "NO", "ans_b": "YES",
        "dim": "2 · Architecture, Modularity & Trade-off Soundness",
        "src": "EXPLICIT_PROMPT",
        "ra": "Model A adds 'trzsz' to 'optimizeDeps.exclude' (patch_a.diff:L24). 'trzsz' is an unrelated pre-existing package in the repository, and Model A fails to target any ZMODEM package for bundler exclusion.",
        "rb": "Model B targets ZMODEM by appending 'zmodem-wasm' to 'optimizeDeps.exclude' at patch_b.diff:L21, properly aiming to prevent bundler pre-compilation for the ZMODEM module."
    },
    # 03
    {
        "crit": "Does the Vite configuration avoid introducing unrequested, pre-existing packages (such as 'trzsz') into 'optimizeDeps.exclude'?",
        "ans_a": "NO", "ans_b": "YES",
        "dim": "5 · Instruction Following & Scope Discipline",
        "src": "INFERRABLE_FROM_ENVIRONMENT",
        "ra": "Model A introduces 'trzsz' into 'optimizeDeps.exclude' (patch_a.diff:L24). 'trzsz' is an unrelated dependency already present in package.json and not part of the requested ZMODEM migration.",
        "rb": "Model B limits its additions in 'optimizeDeps.exclude' strictly to its ZMODEM candidate ('zmodem-wasm') and introduces no unrelated packages (patch_b.diff:L21)."
    },
    # 04
    {
        "crit": "Does the agent's final summary accurately reflect the code changes actually applied in its patch without hallucinating uncommitted configuration changes?",
        "ans_a": "NO", "ans_b": "YES",
        "dim": "9 · Final Summary & Presentation Quality",
        "src": "COMMON_ENGINEERING_KNOWLEDGE",
        "ra": "Model A's final answer claims that it updated 'build/vite/conf.js' to support the new file transfer library by excluding 'trzsz', misrepresenting an unrelated tool as the migration target while deleting the ZMODEM chunk without replacement.",
        "rb": "Model B's final answer accurately reports the changes in its patch (patch_b.diff:L10-21), correctly detailing the replacement of 'zmodem-ts' with 'zmodem-wasm' in both 'manualChunks' and 'optimizeDeps.exclude'."
    },
    # 05
    {
        "crit": "Does the Vite configuration configure the exact package name installed in 'package.json' ('zmodem2-wasm') in 'manualChunks' in 'build/vite/conf.js'?",
        "ans_a": "NO", "ans_b": "NO",
        "dim": "2 · Architecture, Modularity & Trade-off Soundness",
        "src": "REPO_CODE_OR_TESTS",
        "ra": "Model A deletes the 'zmodem-ts' chunk condition without adding 'zmodem2-wasm' (patch_a.diff:L8-14), failing to configure the installed WebAssembly dependency in 'manualChunks'.",
        "rb": "Model B configures 'zmodem-wasm' (patch_b.diff:L11-12) instead of the exact package name declared in package.json ('zmodem2-wasm'), failing to match the installed package."
    },
    # 06
    {
        "crit": "Does the Vite configuration add the exact package name installed in 'package.json' ('zmodem2-wasm') to 'optimizeDeps.exclude' in 'build/vite/conf.js'?",
        "ans_a": "NO", "ans_b": "NO",
        "dim": "2 · Architecture, Modularity & Trade-off Soundness",
        "src": "REPO_CODE_OR_TESTS",
        "ra": "Model A adds 'trzsz' instead of 'zmodem2-wasm' to 'optimizeDeps.exclude' (patch_a.diff:L24), failing to exclude the installed WebAssembly library.",
        "rb": "Model B appends 'zmodem-wasm' (patch_b.diff:L21) rather than the installed 'zmodem2-wasm' dependency to 'optimizeDeps.exclude', failing to match the installed package."
    },
    # 07
    {
        "crit": "Does the implementation preserve the pre-existing 'ironrdp-wasm' entry in 'optimizeDeps.exclude'?",
        "ans_a": "YES", "ans_b": "YES",
        "dim": "4 · Robustness, Safety & API Stability",
        "src": "INFERRABLE_FROM_ENVIRONMENT",
        "ra": "Model A preserves 'ironrdp-wasm' in 'optimizeDeps.exclude' on patch_a.diff:L24 while appending 'trzsz'.",
        "rb": "Model B preserves 'ironrdp-wasm' in 'optimizeDeps.exclude' on patch_b.diff:L21 while appending 'zmodem-wasm'."
    },
    # 08
    {
        "crit": "Does the implementation remove the obsolete 'zmodem-ts' manualChunks reference from 'build/vite/conf.js'?",
        "ans_a": "YES", "ans_b": "YES",
        "dim": "5 · Instruction Following & Scope Discipline",
        "src": "EXPLICIT_PROMPT",
        "ra": "Model A removes the obsolete 'zmodem-ts' manualChunks condition from 'build/vite/conf.js' on patch_a.diff:L8-14.",
        "rb": "Model B removes the obsolete 'zmodem-ts' manualChunks condition from 'build/vite/conf.js' on patch_b.diff:L9-10."
    },
    # 09
    {
        "crit": "Does the implementation maintain valid JavaScript syntax in 'build/vite/conf.js' without syntax errors or unclosed blocks?",
        "ans_a": "YES", "ans_b": "YES",
        "dim": "3 · Codebase Conventions & Utility Reuse",
        "src": "COMMON_ENGINEERING_KNOWLEDGE",
        "ra": "Model A's modifications to 'build/vite/conf.js' (patch_a.diff:L8-25) preserve valid JavaScript syntax and block structure.",
        "rb": "Model B's modifications to 'build/vite/conf.js' (patch_b.diff:L5-22) maintain syntactically valid JavaScript with proper array and function formatting."
    },
    # 10
    {
        "crit": "Does the agent execute the project's test suite or verification commands to validate the build configuration after editing?",
        "ans_a": "NO", "ans_b": "NO",
        "dim": "7 · Verification & Testing Discipline",
        "src": "INFERRABLE_FROM_ENVIRONMENT",
        "ra": "Model A executes no test runner, build script, or verification commands after modifying 'build/vite/conf.js', leaving its changes completely untested.",
        "rb": "Model B does not run the project's test suite or Vite build command after editing 'build/vite/conf.js' to verify that the bundling configuration operates cleanly."
    }
]

async def apply_fix():
    p = await async_playwright().start()
    b = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [pg for pg in b.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url][0]

    print("1. Updating Verifiers via Studio API...")
    update_res = await page.evaluate('''async (rubrics) => {
        const token = await window.Clerk.session.getToken({ skipCache: true });
        const headers = {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json',
            'x-campaign-id': localStorage.getItem('x-campaign-id') || 'camp_75099d23386f4394ab7596a5ea538da8',
            'x-company-id': localStorage.getItem('x-company-id') || 'comp_2fa4115109d741cd94a3c409ed89e61f',
            'x-account-id': localStorage.getItem('x-account-id') || 'acct_85b680d4c5ba49a29f19c173672aebea'
        };

        const taskId = 'task_f5ba2eb1464a4db2831f60a63283341d';
        const vRes = await fetch(`https://api.studio.mercor.com/verifiers/task/${taskId}`, { headers });
        const vData = await vRes.json();
        const verifiers = vData.verifiers || vData;

        const results = [];
        for (let i = 0; i < 10; i++) {
            const v = verifiers[i];
            const r = rubrics[i];
            if (!v) continue;

            const payload = {
                verifier_values: {
                    criteria: r.crit
                },
                verifier_custom_field_values: {
                    dimension: r.dim,
                    source: r.src,
                    answer_a: r.ans_a,
                    reason_a: r.ra,
                    answer_b: r.ans_b,
                    reason_b: r.rb
                }
            };

            const pRes = await fetch(`https://api.studio.mercor.com/verifiers/${v.id}`, {
                method: 'PATCH',
                headers,
                body: JSON.stringify(payload)
            });
            results.push({ id: v.id, status: pRes.status });
        }
        return results;
    }''', RUBRIC_DATA)
    print("Verifiers update result:", update_res)

    print("\n2. Updating Task Custom Fields (Rubrics 1-10 answers and reasons)...")
    cf_update_res = await page.evaluate('''async (rubrics) => {
        const token = await window.Clerk.session.getToken({ skipCache: true });
        const headers = {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json',
            'x-campaign-id': localStorage.getItem('x-campaign-id') || 'camp_75099d23386f4394ab7596a5ea538da8',
            'x-company-id': localStorage.getItem('x-company-id') || 'comp_2fa4115109d741cd94a3c409ed89e61f',
            'x-account-id': localStorage.getItem('x-account-id') || 'acct_85b680d4c5ba49a29f19c173672aebea'
        };

        const taskId = 'task_f5ba2eb1464a4db2831f60a63283341d';
        const patchFields = {};
        for (let i = 0; i < 10; i++) {
            const num = String(i + 1).padStart(2, '0');
            const r = rubrics[i];
            patchFields[`field_ta_rubric_${num}_answer_a`] = r.ans_a;
            patchFields[`field_ta_rubric_${num}_reason_a`] = r.ra;
            patchFields[`field_ta_rubric_${num}_answer_b`] = r.ans_b;
            patchFields[`field_ta_rubric_${num}_reason_b`] = r.rb;
        }

        const tRes = await fetch(`https://api.studio.mercor.com/tasks/${taskId}`, {
            method: 'PATCH',
            headers,
            body: JSON.stringify({ custom_fields: patchFields })
        });
        return { status: tRes.status };
    }''', RUBRIC_DATA)
    print("Task CF update result:", cf_update_res)

    await asyncio.sleep(2)

    print("\n3. Triggering Deliverable AutoQC...")
    run_res = await page.evaluate('''() => {
        const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText && b.innerText.trim() === 'Run AutoQC');
        if (btn) {
            btn.scrollIntoView({ behavior: 'instant', block: 'center' });
            btn.click();
            return { ok: true, text: btn.innerText };
        }
        return { ok: false };
    }''')
    print("Run AutoQC button click:", run_res)

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

        # Detect completion: when runText updates to "just now" or "seconds ago" or isRunning goes False after Compiling
        if not info['isRunning'] and cycle >= 4:
            print("AutoQC execution completed! Settling 3s...")
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

    ss_nav = os.path.join(TASK_DIR, 'final_navigation_checklist_100_percent.png')
    await page.screenshot(path=ss_nav)
    print(f"Saved {ss_nav}")

    await b.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(apply_fix())
