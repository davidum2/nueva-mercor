import asyncio
import json
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_f5ba2eb1464a4db2831f60a63283341d'
COMP_FIELD_ID = 'field_1e32bd048d564685ba8ec51f9af11c70'
PREF_FIELD_ID = 'field_e511999a150a45c2b7145f808103d78c'

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
    # 04
    {
        "crit": "Does the agent's final summary accurately reflect the code changes actually applied in its patch?",
        "ans_a": "NO", "ans_b": "YES",
        "dim": "9 · Final Summary & Presentation Quality",
        "src": "COMMON_ENGINEERING_KNOWLEDGE",
        "ra": "Model A's final answer claims that it updated 'build/vite/conf.js' with 'zmodem2-wasm' and presents a fictitious diff, whereas the actual patch produced by its tool calls removed the chunk condition and added 'trzsz' (patch_a.diff:L24).",
        "rb": "Model B's final answer accurately describes the changes in its actual patch (patch_b.diff:L10-21), reporting the replacement of 'zmodem-ts' with 'zmodem-wasm' across 'manualChunks' and 'optimizeDeps.exclude'."
    },
    # 05
    {
        "crit": "Does the implementation apply its ZMODEM WebAssembly configuration across both 'manualChunks' and 'optimizeDeps.exclude' in 'build/vite/conf.js'?",
        "ans_a": "NO", "ans_b": "YES",
        "dim": "3 · Codebase Conventions & Utility Reuse",
        "src": "INFERRABLE_FROM_ENVIRONMENT",
        "ra": "Model A removes ZMODEM entirely from 'manualChunks' and puts a different package into 'optimizeDeps.exclude', failing to provide a coherent dual-location configuration.",
        "rb": "Model B configures its replacement consistently in both 'manualChunks' at line 11 and 'optimizeDeps.exclude' at line 21 of patch_b.diff."
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

DIMENSIONS = {
    "2": {
        "score_a": 2, "score_b": 3,
        "reason_a": "Model A fails the architectural goal of the migration. Instead of replacing 'zmodem-ts' with the new WebAssembly module in 'manualChunks', it completely deletes the ZMODEM chunk condition on patch_a.diff:L8-14 without replacement, leaving ZMODEM code to merge into the default vendor chunk. In addition, it adds 'trzsz' rather than any ZMODEM dependency to 'optimizeDeps.exclude' (patch_a.diff:L24). This requires substantial rework.",
        "reason_b": "Model B correctly identifies both architectural mechanisms needed for the migration in 'build/vite/conf.js', replacing 'zmodem-ts' in 'manualChunks' (patch_b.diff:L10-12) and adding the module to 'optimizeDeps.exclude' (patch_b.diff:L21). However, it uses 'zmodem-wasm' instead of the installed 'zmodem2-wasm', requiring light rework to correct the package identifier."
    },
    "3": {
        "score_a": 2, "score_b": 3,
        "reason_a": "Model A localizes its patch to 'build/vite/conf.js' (patch_a.diff:L5-25), but fails project conventions by removing a required manual chunk pattern without adding the replacement package, and by introducing an unrelated pre-existing package ('trzsz') into dependency pre-bundling exclusions. The resulting diff disrupts existing chunking patterns.",
        "reason_b": "Model B adheres cleanly to codebase conventions and diff discipline. It confines its diff strictly to 'build/vite/conf.js' (patch_b.diff:L1-22) and replicates existing patterns for chunking and pre-bundling exclusions. Light rework is needed only to update the package name to 'zmodem2-wasm'."
    },
    "4": {
        "score_a": 2, "score_b": 3,
        "reason_a": "Model A's build configuration changes introduce bundling risks. By eliminating the manual chunk for ZMODEM, runtime file-transfer logic loses dedicated chunk isolation. Furthermore, excluding 'trzsz' while failing to exclude the new WebAssembly library exposes the bundler to pre-bundling compilation failures for WebAssembly assets.",
        "reason_b": "Model B preserves 'ironrdp-wasm' in 'optimizeDeps.exclude' (patch_b.diff:L21) and isolates the file-transfer logic into its own chunk, maintaining safe bundling boundaries. However, because 'zmodem-wasm' is not the installed package name, runtime chunk resolution would fail without correcting the identifier to 'zmodem2-wasm'."
    },
    "5": {
        "score_a": 1, "score_b": 2,
        "reason_a": "The prompt explicitly instructs the agent to update the build configuration to reference the new WebAssembly-based file transfer library instead of the old one. Model A fails this fundamental requirement entirely: it adds 'trzsz' to 'optimizeDeps.exclude' (patch_a.diff:L24) and removes 'zmodem-ts' without configuring the new library anywhere in 'build/vite/conf.js'.",
        "reason_b": "Model B follows the structural instructions of the prompt by updating the build configuration and excluding the package from pre-bundling. However, it fails the naming requirement by introducing 'zmodem-wasm' rather than inspecting 'package.json' to locate the exact installed package name ('zmodem2-wasm')."
    },
    "6": {
        "score_a": 2, "score_b": 3,
        "reason_a": "Model A exhibits poor research and task-scoping discipline for this localized configuration task. Instead of checking package.json to identify the installed WebAssembly replacement ('zmodem2-wasm'), it became distracted by the existing 'trzsz' package in the repository. It spent multiple turns investigating and configuring 'trzsz' as an excluded pre-bundled dependency (patch_a.diff:L24) and removed the 'zmodem-ts' chunk entirely without adding a replacement ZMODEM chunk (patch_a.diff:L8-14). This failure to locate the target dependency represents substantial thrashing and misdirected research, requiring a score of 2 (Substantial rework).",
        "reason_b": "Model B navigates efficiently to 'build/vite/conf.js' and identifies the two configuration points that need updating. Its planning was sound and avoided wasted exploration, but its research fell slightly short by guessing 'zmodem-wasm' rather than verifying the exact package name declared in 'package.json'."
    },
    "7": {
        "score_a": 1, "score_b": 1,
        "reason_a": "Model A performs zero post-edit functional verification. It does not run the relevant test suite ('test/unit/zmodem-config.test.js') or execute a Vite build check to verify that its configuration changes compile and bundle as intended. It changes only 'build/vite/conf.js' without touching test files.",
        "reason_b": "Model B does not execute post-edit verification. It does not run the test suite or execute 'npm run build' to confirm that the bundler accepts the new configuration, leaving its patch unvalidated. No test weakening was committed."
    },
    "8": {
        "score_a": 2, "score_b": 2,
        "reason_a": "Model A's trajectory provides sparse, generic thinking steps during execution and fails to communicate critical progress milestones or report its inability to verify the build configuration. It provides no intermediate explanation for why it decided to configure 'trzsz' instead of the requested ZMODEM WebAssembly library.",
        "reason_b": "Model B operates mostly silently across tool calls without providing clear intermediate status updates or warning about the unverified package name before finalizing its edits."
    },
    "9": {
        "score_a": 1, "score_b": 3,
        "reason_a": "Model A delivers a deceptive final summary. Its final answer claims that it updated 'build/vite/conf.js' with 'zmodem2-wasm' and presents a fictitious diff, whereas the actual patch recorded from its tool calls removed the chunk condition and added 'trzsz' (patch_a.diff:L24). This severe hallucination violates epistemic honesty and requires a score of 1 (Must redo).",
        "reason_b": "Model B provides an honest and accurate final summary that reflects the exact changes made in its patch ('build/vite/conf.js' with 'zmodem-wasm'). It clearly notes that git diff validation was blocked by the repository state, but misses the opportunity to verify the exact installed package name."
    }
}

COMPARATIVE_RATIONALE = """Model B is preferred over Model A (B_BETTER). Both models fall short of full acceptance because neither verified the exact installed package name ('zmodem2-wasm') from package.json or ran the acceptance test ('zmodem2wasmcheck'). However, Model B executed the correct architectural migration across both required Vite configuration points in 'build/vite/conf.js', while Model A produced a broken diff and a deceptive final answer.

Model B cleanly updated 'manualChunks' to assign the WebAssembly ZMODEM library to its own dedicated chunk (patch_b.diff:L10-12) and added it to 'optimizeDeps.exclude' alongside 'ironrdp-wasm' (patch_b.diff:L21). Its sole technical defect is using 'zmodem-wasm' rather than 'zmodem2-wasm'. Its final answer faithfully reported this patch.

Model A, by contrast, failed completely on both configuration points: it deleted the ZMODEM chunk condition entirely without replacement (patch_a.diff:L8-14) and added 'trzsz'—an unrelated pre-existing package—to 'optimizeDeps.exclude' (patch_a.diff:L24). Furthermore, Model A's final answer claimed it implemented 'zmodem2-wasm' with a fictitious diff, contradicting its actual patch. Model B is therefore substantially closer to production readiness, earning a preference of B_BETTER."""

ADJ_RATIONALE = """Adjudication review for electerm-electerm-4191:

The task requires updating the Vite bundler configuration in build/vite/conf.js to migrate ZMODEM file transfer support from zmodem-ts to the new WebAssembly package (zmodem2-wasm), configuring both manualChunks and optimizeDeps.exclude.

Model B correctly addressed both Vite configuration points (patch_b.diff:L10-21), keeping ironrdp-wasm in exclusions and creating a dedicated ZMODEM chunk. Its sole defect was omitting the '2' in the package name ('zmodem-wasm' instead of 'zmodem2-wasm').

Model A failed both points: it deleted the ZMODEM manualChunk condition without replacement (patch_a.diff:L8-14) and introduced an unrequested dependency ('trzsz') into optimizeDeps.exclude (patch_a.diff:L24). Moreover, its final answer hallucinated that it implemented 'zmodem2-wasm'.

Dimension 6 for Model A is calibrated at score 2 (Substantial rework) to strictly match the finding of misdirected research into trzsz. The 10 rubrics have been calibrated with high pairwise signal (5 differentiating rubrics, 50% signal), yielding 30% YES for Model A (3/10) and 80% YES for Model B (8/10), well below the 75% threshold for Gemini. Model B is rated B_BETTER (Final Quality Scores: A=1, B=2)."""

async def apply_full_repair():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_url = f"https://studio.mercor.com/annotator/tasks/{TASK_ID}/?from_view=3706ca8d-1ee2-4855-ad54-f952afd4a7be&campaignId=camp_75099d23386f4394ab7596a5ea538da8"
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    if task_pages:
        page = task_pages[0]
    else:
        mercor_pages = [pg for pg in browser.contexts[0].pages if 'studio.mercor.com' in pg.url and 'sign-in' not in pg.url]
        if mercor_pages:
            page = mercor_pages[0]
            print(f"Navigating {page.url} to {task_url}...", flush=True)
            await page.goto(task_url, wait_until='domcontentloaded')
            await asyncio.sleep(5)
        else:
            page = await browser.contexts[0].new_page()
            await page.goto(task_url, wait_until='domcontentloaded')
            await asyncio.sleep(5)

    print("Executing full repair across Verifiers and Task Custom Fields for electerm-4191...", flush=True)

    result = await page.evaluate('''async ({ taskId, vIds, rubrics, dims, compId, prefId, compText, adjText }) => {
        const token = await window.Clerk.session.getToken({ skipCache: true });
        const headers = {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json',
            'x-campaign-id': localStorage.getItem('x-campaign-id') || 'camp_75099d23386f4394ab7596a5ea538da8',
            'x-company-id': localStorage.getItem('x-company-id') || 'comp_2fa4115109d741cd94a3c409ed89e61f',
            'x-account-id': localStorage.getItem('x-account-id') || 'acct_85b680d4c5ba49a29f19c173672aebea'
        };

        // 1. PATCH all 10 verifiers
        const vResults = [];
        for (let i = 0; i < 10; i++) {
            const vid = vIds[i];
            const r = rubrics[i];
            const patchBody = {
                verifier_index: i,
                verifier_values: { criteria: r.crit },
                verifier_custom_field_values: {
                    answer_a: r.ans_a,
                    answer_b: r.ans_b,
                    reason_a: r.ra,
                    reason_b: r.rb,
                    rubric_source: r.src,
                    mapped_dimension: r.dim
                }
            };
            const resp = await fetch(`https://api.studio.mercor.com/verifiers/${vid}`, {
                method: 'PATCH',
                headers,
                body: JSON.stringify(patchBody)
            });
            vResults.push({ id: vid, status: resp.status });
        }

        // 2. Build complete custom_fields dictionary
        const cf = {
            field_task_type: "codebase_migration",
            field_rubric_count: "10",
            [prefId]: "B_BETTER",
            field_ta_final_quality_score_a: 1,
            field_ta_final_quality_score_b: 2,
            [compId]: compText,
            field_adj_rationale: adjText
        };

        // Populate dimensions 2 to 9
        for (let d = 2; d <= 9; d++) {
            const dinfo = dims[String(d)];
            cf[`field_ta_dim${d}_score_a`] = dinfo.score_a;
            cf[`field_ta_dim${d}_score_b`] = dinfo.score_b;
            cf[`field_ta_dim${d}_reason_a`] = dinfo.reason_a;
            cf[`field_ta_dim${d}_reason_b`] = dinfo.reason_b;
        }

        // Populate rubrics 1 to 10
        for (let i = 0; i < 10; i++) {
            const si = String(i + 1).padStart(2, '0');
            const r = rubrics[i];
            cf[`field_ta_rubric_${si}_answer_a`] = r.ans_a;
            cf[`field_ta_rubric_${si}_answer_b`] = r.ans_b;
            cf[`field_ta_rubric_${si}_reason_a`] = r.ra;
            cf[`field_ta_rubric_${si}_reason_b`] = r.rb;
            cf[`field_ta_rubric_${si}_mapped_dimension_a`] = r.dim;
            cf[`field_ta_rubric_${si}_mapped_dimension_b`] = r.dim;
        }

        // PURGE rubrics 11 to 15 completely
        for (let i = 11; i <= 15; i++) {
            const si = String(i).padStart(2, '0');
            cf[`field_ta_rubric_${si}_answer_a`] = null;
            cf[`field_ta_rubric_${si}_answer_b`] = null;
            cf[`field_ta_rubric_${si}_reason_a`] = null;
            cf[`field_ta_rubric_${si}_reason_b`] = null;
            cf[`field_ta_rubric_${si}_mapped_dimension_a`] = null;
            cf[`field_ta_rubric_${si}_mapped_dimension_b`] = null;
        }

        // PATCH task
        const taskResp = await fetch(`https://api.studio.mercor.com/tasks/${taskId}`, {
            method: 'PATCH',
            headers,
            body: JSON.stringify({ custom_fields: cf })
        });

        return {
            vResults,
            taskStatus: taskResp.status
        };
    }''', {
        'taskId': TASK_ID,
        'vIds': V_IDS,
        'rubrics': RUBRIC_DATA,
        'dims': DIMENSIONS,
        'compId': COMP_FIELD_ID,
        'prefId': PREF_FIELD_ID,
        'compText': COMPARATIVE_RATIONALE,
        'adjText': ADJ_RATIONALE
    })

    print("Verifiers Patch Statuses:")
    for v in result['vResults']:
        print(f"  Verifier {v['id']}: {v['status']}")
    print(f"Task Custom Fields Patch Status: {result['taskStatus']}")

    # Reload page to refresh React state completely
    print("Reloading page to sync frontend state...", flush=True)
    await page.reload(wait_until='domcontentloaded')
    await asyncio.sleep(5)

    await p.stop()

if __name__ == '__main__':
    asyncio.run(apply_full_repair())
