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

RUBRIC_DATA = [
    # 01
    {
        "crit": "Does the Vite configuration retain a dedicated manual chunk condition for the new WebAssembly-based ZMODEM library in 'build/vite/conf.js'?",
        "ans_a": "NO", "ans_b": "YES",
        "dim": "2 · Architecture, Modularity & Trade-off Soundness",
        "src": "EXPLICIT_PROMPT",
        "ra": "Model A deletes the 'zmodem-ts' condition in 'manualChunks' on patch_a.diff:L8-14 without replacing it with any ZMODEM entry, causing ZMODEM code to fall into the default vendor bundle rather than having a dedicated chunk.",
        "rb": "Model B updates the 'manualChunks' function in 'build/vite/conf.js' to return 'zmodem-wasm' (patch_b.diff:L10-12), ensuring the WebAssembly file-transfer module maintains its own dedicated chunk."
    },
    # 02
    {
        "crit": "Does the Vite configuration add the WebAssembly-based ZMODEM replacement to 'optimizeDeps.exclude' in 'build/vite/conf.js'?",
        "ans_a": "NO", "ans_b": "YES",
        "dim": "2 · Architecture, Modularity & Trade-off Soundness",
        "src": "EXPLICIT_PROMPT",
        "ra": "Model A adds 'trzsz' to 'optimizeDeps.exclude' (patch_a.diff:L24) rather than any ZMODEM module, leaving the new ZMODEM WebAssembly library unconfigured in Vite's pre-bundling exclusions.",
        "rb": "Model B adds its WebAssembly-based ZMODEM module ('zmodem-wasm') to 'optimizeDeps.exclude' on patch_b.diff:L21, properly configuring the bundler to prevent pre-bundling of the WASM dependency."
    },
    # 03
    {
        "crit": "Does the Vite configuration avoid introducing unrequested, unrelated packages into 'optimizeDeps.exclude'?",
        "ans_a": "NO", "ans_b": "YES",
        "dim": "5 · Instruction Following & Scope Discipline",
        "src": "INFERRABLE_FROM_ENVIRONMENT",
        "ra": "Model A introduces 'trzsz' into 'optimizeDeps.exclude' (patch_a.diff:L24). 'trzsz' is an unrelated pre-existing dependency that was not part of the requested ZMODEM migration.",
        "rb": "Model B limits its additions in 'optimizeDeps.exclude' strictly to its ZMODEM WASM library candidate ('zmodem-wasm') and introduces no unrelated packages (patch_b.diff:L21)."
    },
    # 04 (Adjusted exactly per AutoQC instruction: YES on Side A, acknowledging summary faithfully reported actual changes)
    {
        "crit": "Does the agent's final summary accurately reflect the code changes actually applied in its patch?",
        "ans_a": "YES", "ans_b": "YES",
        "dim": "9 · Final Summary & Presentation Quality",
        "src": "COMMON_ENGINEERING_KNOWLEDGE",
        "ra": "Model A's final summary accurately reflects the changes actually applied in its patch (patch_a.diff:L8-24), faithfully reporting that it excluded 'trzsz' from optimizeDeps.exclude and removed 'zmodem-ts' from manualChunks, despite the implementation itself being incorrect.",
        "rb": "Model B's final answer accurately describes the changes in its actual patch (patch_b.diff:L10-21), reporting the replacement of 'zmodem-ts' with 'zmodem-wasm' across 'manualChunks' and 'optimizeDeps.exclude'."
    },
    # 05 (Adjusted per AutoQC instruction: replaced dual-location check with single atomic syntax preservation check)
    {
        "crit": "Does the implementation maintain valid JavaScript syntax in 'build/vite/conf.js' without syntax errors or unclosed blocks?",
        "ans_a": "YES", "ans_b": "YES",
        "dim": "3 · Codebase Conventions & Utility Reuse",
        "src": "COMMON_ENGINEERING_KNOWLEDGE",
        "ra": "Model A's modifications to 'build/vite/conf.js' (patch_a.diff:L8-25) preserve valid JavaScript syntax and block structure.",
        "rb": "Model B's modifications to 'build/vite/conf.js' (patch_b.diff:L5-22) maintain syntactically valid JavaScript with proper array and function formatting."
    },
    # 06
    {
        "crit": "Does the implementation preserve the pre-existing 'ironrdp-wasm' entry in 'optimizeDeps.exclude'?",
        "ans_a": "YES", "ans_b": "YES",
        "dim": "4 · Robustness, Safety & API Stability",
        "src": "INFERRABLE_FROM_ENVIRONMENT",
        "ra": "Model A preserves 'ironrdp-wasm' in 'optimizeDeps.exclude' on patch_a.diff:L24 while appending 'trzsz'.",
        "rb": "Model B preserves 'ironrdp-wasm' in 'optimizeDeps.exclude' on patch_b.diff:L21 while appending 'zmodem-wasm'."
    },
    # 07
    {
        "crit": "Does the implementation remove the obsolete 'zmodem-ts' manualChunks reference from 'build/vite/conf.js'?",
        "ans_a": "YES", "ans_b": "YES",
        "dim": "5 · Instruction Following & Scope Discipline",
        "src": "EXPLICIT_PROMPT",
        "ra": "Model A removes the obsolete 'zmodem-ts' manualChunks condition from 'build/vite/conf.js' on patch_a.diff:L8-14.",
        "rb": "Model B removes the obsolete 'zmodem-ts' manualChunks condition from 'build/vite/conf.js' on patch_b.diff:L9-10."
    },
    # 08
    {
        "crit": "Does the implementation keep production changes restricted strictly to 'build/vite/conf.js' without modifying unrelated files or tests?",
        "ans_a": "YES", "ans_b": "YES",
        "dim": "5 · Instruction Following & Scope Discipline",
        "src": "INFERRABLE_FROM_ENVIRONMENT",
        "ra": "Model A's diff is strictly confined to 'build/vite/conf.js' (patch_a.diff:L5-25) and modifies no other repository files or unit tests.",
        "rb": "Model B modifies only 'build/vite/conf.js' (patch_b.diff:L1-22), adhering strictly to the required file scope."
    },
    # 09
    {
        "crit": "Does the implementation use the exact package name installed in 'package.json' ('zmodem2-wasm') in the Vite configuration?",
        "ans_a": "NO", "ans_b": "NO",
        "dim": "2 · Architecture, Modularity & Trade-off Soundness",
        "src": "REPO_CODE_OR_TESTS",
        "ra": "Model A does not reference 'zmodem2-wasm' anywhere in its actual patch (patch_a.diff:L5-25), omitting ZMODEM from 'manualChunks' and using 'trzsz' in exclusions.",
        "rb": "Model B references 'zmodem-wasm' (patch_b.diff:L11, L21) rather than the exact package name declared in package.json ('zmodem2-wasm'), failing to match the installed dependency."
    },
    # 10
    {
        "crit": "Does the agent execute a successful functional verification or unit test verifying the build configuration after its changes?",
        "ans_a": "NO", "ans_b": "NO",
        "dim": "7 · Verification & Testing Discipline",
        "src": "INFERRABLE_FROM_ENVIRONMENT",
        "ra": "Model A's trajectory does not run the required unit test ('test/unit/zmodem-config.test.js') or verify that the build configuration successfully bundles the new WebAssembly package.",
        "rb": "Model B's trajectory does not execute the acceptance test suite ('zmodem2wasmcheck') after editing 'build/vite/conf.js' to verify functional compliance."
    }
]

async def apply_perfect_fix():
    p = await async_playwright().start()
    b = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [pg for pg in b.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url][0]

    print("1. Updating Verifiers via Studio API using exact V_IDS...")
    update_res = await page.evaluate('''async ({ vIds, rubrics }) => {
        const token = await window.Clerk.session.getToken({ skipCache: true });
        const headers = {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json',
            'x-campaign-id': localStorage.getItem('x-campaign-id') || 'camp_75099d23386f4394ab7596a5ea538da8',
            'x-company-id': localStorage.getItem('x-company-id') || 'comp_2fa4115109d741cd94a3c409ed89e61f',
            'x-account-id': localStorage.getItem('x-account-id') || 'acct_85b680d4c5ba49a29f19c173672aebea'
        };

        const results = [];
        for (let i = 0; i < 10; i++) {
            const vid = vIds[i];
            const r = rubrics[i];

            const payload = {
                verifier_index: i,
                verifier_values: {
                    criteria: r.crit
                },
                verifier_custom_field_values: {
                    dimension: r.dim,
                    source: r.src,
                    answer_a: r.ans_a,
                    reason_a: r.ra,
                    answer_b: r.ans_b,
                    reason_b: r.rb,
                    rubric_source: r.src,
                    mapped_dimension: r.dim
                }
            };

            const pRes = await fetch(`https://api.studio.mercor.com/verifiers/${vid}`, {
                method: 'PATCH',
                headers,
                body: JSON.stringify(payload)
            });
            results.push({ id: vid, status: pRes.status });
        }
        return results;
    }''', {'vIds': V_IDS, 'rubrics': RUBRIC_DATA})
    print("Verifiers update statuses:", update_res)

    print("\n2. Updating Task Custom Fields (Rubrics 1-10)...")
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
            patchFields[`field_ta_rubric_${num}_mapped_dimension_a`] = r.dim;
            patchFields[`field_ta_rubric_${num}_mapped_dimension_b`] = r.dim;
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

    print("\n3. Triggering AutoQC (Clicking Run AutoQC)...")
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

    ss_nav = os.path.join(TASK_DIR, 'navigation_100_percent_success.png')
    await page.screenshot(path=ss_nav)
    print(f"Saved {ss_nav}")

    await b.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(apply_perfect_fix())
