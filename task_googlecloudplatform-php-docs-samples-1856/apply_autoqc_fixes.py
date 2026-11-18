import asyncio
import json
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'
VERIFIER_13_ID = 'ver_c1edf3d7330449e1b351286330f42ebb'

NEW_DIM3_A = "Model A follows official Google Cloud sample conventions and diff cleanliness flawlessly. In patch_a.diff, the diff is clean, compact, and completely free of code duplication or extraneous edits to existing repository files. It introduces only the single new sample file without whitespace noise or dead code. The implementation encloses the logic within standard region tags '# [START dlp_deidentify_cloud_storage]' and '# [END dlp_deidentify_cloud_storage]' (patch_a.diff:L33, L159), declares the proper namespace Google\\Cloud\\Samples\\Dlp (patch_a.diff:L31), provides comprehensive PHPDoc type annotations for all 8 parameters (patch_a.diff:L50-58), and appends the standard CLI sample execution harness calling execute_sample (patch_a.diff:L162-163)."

NEW_DIM3_B = "Model B exhibits an acceptable diff shape that introduces only the new sample file in patch_b.diff without duplicating existing files or littering whitespace noise. However, in terms of clean code and convention adherence, its parameter documentation reflects the broken 9-parameter signature (patch_b.diff:L57) by documenting an extraneous parameter, and the Apache license header year is set inconsistently to 2026 on line 10. While region tags and namespace structure are included (patch_b.diff:L33, L141), the signature mismatch directly degrades code readability and convention compliance."

NEW_R13_REASON_A = "Model A states in final_answer_a.txt:L1 that it created the 'required deidentify_cloud_storage function' and outlines the configuration and polling workflow, but it omits the formal 8-parameter function signature and does not enumerate the required parameter names ($callingProjectId, $inputGcsUri, etc.) in its deliverable summary."

async def apply_fixes():
    print("Connecting to browser...", flush=True)
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]
    
    result = await page.evaluate("""async ({ taskId, ver13Id, dim3A, dim3B, r13A }) => {
        const getHeaders = async () => {
            const token = await window.Clerk.session.getToken({ skipCache: true });
            return {
                'Authorization': 'Bearer ' + token,
                'Content-Type': 'application/json',
                'x-campaign-id': localStorage.getItem('x-campaign-id') || 'camp_75099d23386f4394ab7596a5ea538da8',
                'x-company-id': localStorage.getItem('x-company-id') || 'comp_2fa4115109d741cd94a3c409ed89e61f',
                'x-account-id': localStorage.getItem('x-account-id') || 'acct_85b680d4c5ba49a29f19c173672aebea'
            };
        };

        // 1. Update Verifier 13 via API
        const vHeaders = await getHeaders();
        const vPatchR = await fetch(`https://api.studio.mercor.com/verifiers/${ver13Id}`, {
            method: 'PATCH',
            headers: vHeaders,
            body: JSON.stringify({
                verifier_custom_field_values: {
                    answer_a: "NO",
                    reason_a: r13A
                }
            })
        });

        // 2. Update Task custom fields via API
        const tHeaders = await getHeaders();
        const custom_fields = {
            field_ta_dim3_reason_a: dim3A,
            field_ta_dim3_reason_b: dim3B,
            field_ta_rubric_13_answer_a: "NO",
            field_ta_rubric_13_reason_a: r13A
        };
        const tPatchR = await fetch(`https://api.studio.mercor.com/tasks/${taskId}`, {
            method: 'PATCH',
            headers: tHeaders,
            body: JSON.stringify({ custom_fields })
        });

        // 3. Update DOM textareas with React native setter
        const textareas = Array.from(document.querySelectorAll('textarea'));
        const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
            window.HTMLTextAreaElement.prototype, "value"
        ).set;

        const updateField = (fieldId, val) => {
            const target = textareas.find(t => {
                const key = Object.keys(t).find(k => k.startsWith('__reactFiber$'));
                let cur = key ? t[key] : null;
                while (cur) {
                    if (cur.memoizedProps && cur.memoizedProps.fieldDef && cur.memoizedProps.fieldDef.field_id === fieldId) {
                        return true;
                    }
                    cur = cur.return;
                }
                return false;
            });
            if (target) {
                nativeInputValueSetter.call(target, val);
                target.dispatchEvent(new Event('input', { bubbles: true }));
                target.dispatchEvent(new Event('change', { bubbles: true }));
                return true;
            }
            return false;
        };

        const domDim3A = updateField('field_ta_dim3_reason_a', dim3A);
        const domDim3B = updateField('field_ta_dim3_reason_b', dim3B);
        const domR13A = updateField('field_ta_rubric_13_reason_a', r13A);

        return {
            verifierPatchStatus: vPatchR.status,
            taskPatchStatus: tPatchR.status,
            domDim3A,
            domDim3B,
            domR13A
        };
    }""", {
        "taskId": TASK_ID,
        "ver13Id": VERIFIER_13_ID,
        "dim3A": NEW_DIM3_A,
        "dim3B": NEW_DIM3_B,
        "r13A": NEW_R13_REASON_A
    })

    print("Fixes Applied Result:", json.dumps(result, indent=2), flush=True)

    # Click Save Changes
    save_btn = await page.query_selector('button:has-text("Save Changes")')
    if save_btn:
        print("Clicking Save Changes button...", flush=True)
        await save_btn.click()
        await asyncio.sleep(2)

    # Click Run AutoQC button
    run_btn = page.locator('button:has-text("Run AutoQC")')
    if await run_btn.count() > 0:
        print("Triggering Run AutoQC...", flush=True)
        await run_btn.first.click()
        print("AutoQC triggered. Waiting 5s...", flush=True)
        await asyncio.sleep(5)
        
    await page.screenshot(path='autoqc_rerun_started.png')
    print("Saved autoqc_rerun_started.png", flush=True)

    await p.stop()
    print("Done!", flush=True)

if __name__ == '__main__':
    asyncio.run(apply_fixes())
