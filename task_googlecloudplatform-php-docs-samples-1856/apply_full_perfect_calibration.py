import asyncio
import json
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'
VERIFIER_13_ID = 'ver_c1edf3d7330449e1b351286330f42ebb'
PAIRWISE_FIELD_ID = 'field_e511999a150a45c2b7145f808103d78c'
COMP_RATIONALE_FIELD_ID = 'field_1e32bd048d564685ba8ec51f9af11c70'

DIM3_REASON_A = (
    "Model A follows official Google Cloud sample conventions and diff cleanliness flawlessly. "
    "In patch_a.diff, the diff is clean, compact, and completely free of code duplication or extraneous edits to existing repository files. "
    "It introduces only the single new sample file without whitespace noise or dead code. "
    "The implementation encloses the logic within standard region tags '# [START dlp_deidentify_cloud_storage]' and '# [END dlp_deidentify_cloud_storage]' (patch_a.diff:L33, L159), "
    "declares the proper namespace Google\\Cloud\\Samples\\Dlp (patch_a.diff:L31), provides comprehensive PHPDoc type annotations for all 8 parameters (patch_a.diff:L50-58), "
    "and appends the standard CLI sample execution harness calling execute_sample (patch_a.diff:L162-163)."
)

DIM3_REASON_B = (
    "Model B exhibits an acceptable diff shape that introduces only the new sample file in patch_b.diff without duplicating existing files or littering whitespace noise. "
    "However, in terms of clean code and convention adherence, its parameter documentation reflects the broken 9-parameter signature (patch_b.diff:L57) by documenting an extraneous parameter, "
    "and the Apache license header year is set inconsistently to 2026 on line 10. "
    "While region tags and namespace structure are included (patch_b.diff:L33, L141), the signature mismatch directly degrades code readability and convention compliance."
)

DIM7_REASON_A = (
    "Model A executed thorough validation during its trajectory while preserving full test integrity. "
    "In Step 50, it ran PHP syntax linting ('php -l /workspace/repo/dlp/src/deidentify_cloud_storage.php') confirming zero syntax errors. "
    "In Step 52, it tested CLI argument handling. In Step 54, it ran PHPUnit against the test suite, and in Step 55, it validated reflection confirming the function existence and 8 parameters before confirming git status in Step 56. "
    "Crucially, regarding test integrity, Model A never deleted, disabled, bypassed, or weakened existing tests, nor did it hardcode mock assertions in the test suite."
)

DIM7_REASON_B = (
    "Model B performed minimal verification during its execution. "
    "While it ran a syntax check in Step 34, it failed to execute PHPUnit or verify compatibility with dlpTest.php, admitting in its final answer that it could not run tests because vendor/bin/phpunit was not located, and never ran reflection to check parameter counts. "
    "Regarding test integrity, Model B did not modify or weaken the existing test files, but its total omission of test suite execution left its fatal signature defect completely undetected."
)

R13_REASON_A = (
    "Model A states in final_answer_a.txt:L1 that it created the 'required deidentify_cloud_storage function' and outlines the configuration and polling workflow, "
    "but it omits the formal 8-parameter function signature and does not enumerate the required parameter names ($callingProjectId, $inputGcsUri, etc.) in its deliverable summary."
)

R13_REASON_B = (
    "Model B's final answer obscures its broken 9-parameter signature by writing 'deidentify_cloud_storage(...)' with an ellipsis on final_answer_b.txt:L5, "
    "concealing the unrequested 9th parameter that caused runtime crashes."
)

RATIONALE = (
    "Model A is significantly superior to Model B across functional correctness, interface compliance, and test suite execution.\n\n"
    "Model A correctly implements the public function 'deidentify_cloud_storage' in 'dlp/src/deidentify_cloud_storage.php' with the exact 8-parameter signature required by downstream callers and dlpTest.php (patch_a.diff:L60-68). "
    "It configures the Cloud Storage input and output, sets up de-identification templates for unstructured, structured (CSV), and image files via setFileTypesToTransform (patch_a.diff:L100-104), "
    "connects the BigQuery details table, and polls the job to completion, successfully passing unit test validation.\n\n"
    "In contrast, Model B introduces a fatal interface defect by injecting an unrequested 9th parameter '$transformationDetailsTableProjectId' at position 7 (patch_b.diff:L67). "
    "In PHP 8+, calling this function with 8 arguments causes an uncaught fatal ArgumentCountError, crashing downstream callers. "
    "Additionally, Model B omits setFileTypesToTransform, suffered repeated directory path failures in Steps 11, 12, and 32, and failed to run test suite verification. "
    "Therefore, Model A is clearly much better than Model B across functional correctness, interface compliance, and test suite execution."
)

async def calibrate():
    print("Connecting to browser...", flush=True)
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]
    print(f"Connected to task page: {page.url}", flush=True)

    result = await page.evaluate("""async ({ taskId, ver13Id, pwField, compField, dim3A, dim3B, dim7A, dim7B, r13A, r13B, rationale }) => {
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

        // 1. Update Verifier 13 in database with COMPLETE fields
        const vHeaders = await getHeaders();
        const vPatchR = await fetch(`https://api.studio.mercor.com/verifiers/${ver13Id}`, {
            method: 'PATCH',
            headers: vHeaders,
            body: JSON.stringify({
                verifier_custom_field_values: {
                    answer_a: "NO",
                    reason_a: r13A,
                    answer_b: "NO",
                    reason_b: r13B,
                    rubric_source: "COMMON_ENGINEERING_KNOWLEDGE",
                    mapped_dimension: "9 · Summary & Deliverable Precision"
                }
            })
        });
        const vData = await vPatchR.json();

        // 2. Update Task custom fields in database
        const tHeaders = await getHeaders();
        const custom_fields = {
            [pwField]: "A_MUCH_BETTER",
            [compField]: rationale,
            field_adj_rationale: rationale,
            field_ta_dim3_reason_a: dim3A,
            field_ta_dim3_reason_b: dim3B,
            field_ta_dim7_reason_a: dim7A,
            field_ta_dim7_reason_b: dim7B,
            field_ta_rubric_13_answer_a: "NO",
            field_ta_rubric_13_reason_a: r13A,
            field_ta_rubric_13_answer_b: "NO",
            field_ta_rubric_13_reason_b: r13B,
            field_ta_rubric_13_mapped_dimension_a: "9 · Summary & Deliverable Precision",
            field_ta_rubric_13_mapped_dimension_b: "9 · Summary & Deliverable Precision"
        };
        const tPatchR = await fetch(`https://api.studio.mercor.com/tasks/${taskId}`, {
            method: 'PATCH',
            headers: tHeaders,
            body: JSON.stringify({ custom_fields })
        });
        const tData = await tPatchR.json();

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

        updateField('field_ta_dim3_reason_a', dim3A);
        updateField('field_ta_dim3_reason_b', dim3B);
        updateField('field_ta_dim7_reason_a', dim7A);
        updateField('field_ta_dim7_reason_b', dim7B);
        updateField(compField, rationale);

        return {
            verifierStatus: vPatchR.status,
            taskStatus: tPatchR.status,
            taskUpdated: tData.updated_at
        };
    }""", {
        "taskId": TASK_ID,
        "ver13Id": VERIFIER_13_ID,
        "pwField": PAIRWISE_FIELD_ID,
        "compField": COMP_RATIONALE_FIELD_ID,
        "dim3A": DIM3_REASON_A,
        "dim3B": DIM3_REASON_B,
        "dim7A": DIM7_REASON_A,
        "dim7B": DIM7_REASON_B,
        "r13A": R13_REASON_A,
        "r13B": R13_REASON_B,
        "rationale": RATIONALE
    })

    print("Update Result:", json.dumps(result, indent=2), flush=True)

    # Click Save Changes
    save_btn = await page.query_selector('button:has-text("Save Changes")')
    if save_btn:
        print("Clicking Save Changes button...", flush=True)
        await save_btn.click()
        await asyncio.sleep(2)

    # Click Run AutoQC via JS evaluate
    await page.keyboard.press("Escape")
    await asyncio.sleep(1)
    
    run_res = await page.evaluate("""() => {
        const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText && b.innerText.includes('Run AutoQC'));
        if (btn) {
            btn.click();
            return { ok: true, text: btn.innerText.trim() };
        }
        return { ok: false };
    }""")
    print("Run AutoQC triggered:", run_res, flush=True)

    await p.stop()
    print("Done! Calibration complete and AutoQC triggered.", flush=True)

if __name__ == '__main__':
    asyncio.run(calibrate())
