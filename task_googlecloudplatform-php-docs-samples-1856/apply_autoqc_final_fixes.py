import asyncio
import json
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'
VERIFIER_10_ID = 'ver_4af2b63c2c864e39888d96d5eee36984'
COMPARATIVE_FIELD_ID = 'field_1e32bd048d564685ba8ec51f9af11c70'

v10_criteria = "Did all terminal commands execute without failing due to a non-existent working directory?"
v10_reason_a = "Model A navigated the repository cleanly in /workspace/repo without any command failing due to a non-existent working directory across Steps 1 through 28."
v10_reason_b = "Model B suffered command failures caused by non-existent working directories, failing with 'No such file or directory' when executing commands in non-existent paths in Step 11, Step 12, and Step 32."

dim3_reason_b = "Model B exhibits acceptable code structure, correct Google Cloud region tags, clean indentation, and diff cleanliness with no code duplication. However, its parameter documentation reflects a broken 9-parameter signature by documenting an extraneous parameter ($transformationDetailsTableProjectId) on patch_b.diff:L53. Because this signature mismatch introduces an interface defect that directly degrades code readability and API convention compliance, Model B is scored 3 rather than a higher score."

dim7_reason_a = "Model A executed thorough validation during its trajectory while preserving full test integrity. In Step 50, it ran PHP syntax linting ('php -l /workspace/repo/dlp/src/deidentify_cloud_storage.php') confirming zero syntax errors. In Step 52, it tested CLI argument handling. In Step 54, it ran PHPUnit against the test suite, with all unit tests executing successfully and passing with zero failures and zero errors. In Step 55, it validated reflection confirming the function existence and 8 parameters before confirming clean git status in Step 56. Crucially, regarding test integrity, Model A never deleted, disabled, bypassed, or weakened existing tests, nor did it hardcode mock assertions in the test suite."

dim7_reason_b = "Model B executed minimal syntax linting ('php -l') in Step 34, but completely omitted test suite verification. It failed to locate or execute PHPUnit, never verified compatibility with dlpTest.php, and never ran reflection to check parameter counts, leaving its fatal signature defect completely undetected. While its diff does not delete or weaken existing tests, Model B's complete omission of test execution warrants a minimal score of 1 for Verification & Testing Rigor."

comparative_rationale = """Model A is significantly superior to Model B across functional correctness, interface compliance, and test suite execution.

Model A correctly implements the public function 'deidentify_cloud_storage' in 'dlp/src/deidentify_cloud_storage.php' with the exact 8-parameter signature required by downstream callers and dlpTest.php (patch_a.diff:L60-68). It configures the Cloud Storage input and output, sets up de-identification templates for unstructured, structured (CSV), and image files via setFileTypesToTransform (patch_a.diff:L100-104), connects the BigQuery details table, and polls the job to completion. In Step 54, Model A validated its implementation by running PHPUnit, with all unit tests passing with zero failures and zero errors.

In contrast, Model B introduces a fatal interface defect by injecting an unrequested 9th parameter '$transformationDetailsTableProjectId' at position 7 (patch_b.diff:L67). In PHP 8+, calling this function with 8 arguments causes an uncaught fatal ArgumentCountError, crashing downstream callers. Additionally, Model B omits setFileTypesToTransform, suffered repeated directory path failures in Steps 11, 12, and 32, and failed to run test suite verification. Therefore, Model A is clearly much better than Model B across functional correctness, interface compliance, and test suite execution."""

async def apply_fixes():
    print("Connecting to browser...", flush=True)
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    # Close any overlays first
    await page.evaluate("""() => {
        document.querySelectorAll('[data-radix-popper-content-wrapper], [data-radix-focus-guard], [role="menu"], [role="listbox"]').forEach(el => el.remove());
        document.querySelectorAll('div[style*="pointer-events"]').forEach(el => el.style.pointerEvents = 'auto');
    }""")
    await page.keyboard.press("Escape")
    await asyncio.sleep(1)

    # 1. Update Verifier 10 via API
    v_res = await page.evaluate("""async ({ vId, crit, rA, rB }) => {
        const token = await window.Clerk.session.getToken({ skipCache: true });
        const headers = {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json',
            'x-campaign-id': localStorage.getItem('x-campaign-id') || 'camp_75099d23386f4394ab7596a5ea538da8',
            'x-company-id': localStorage.getItem('x-company-id') || 'comp_2fa4115109d741cd94a3c409ed89e61f',
            'x-account-id': localStorage.getItem('x-account-id') || 'acct_85b680d4c5ba49a29f19c173672aebea'
        };

        const res = await fetch(`https://api.studio.mercor.com/verifiers/${vId}`, {
            method: 'PATCH',
            headers,
            body: JSON.stringify({
                verifier_values: { criteria: crit },
                verifier_custom_field_values: {
                    answer_a: "YES",
                    answer_b: "NO",
                    reason_a: rA,
                    reason_b: rB,
                    rubric_source: "COMMON_ENGINEERING_KNOWLEDGE",
                    mapped_dimension: "6 · Planning, Research & Exploration"
                }
            })
        });
        return { status: res.status, data: await res.json() };
    }""", { 'vId': VERIFIER_10_ID, 'crit': v10_criteria, 'rA': v10_reason_a, 'rB': v10_reason_b })
    print("Verifier 10 PATCH status:", v_res['status'], flush=True)

    # 2. Update task custom fields via API
    patch_fields = {
        'field_ta_dim3_score_b': 3,
        'field_ta_dim3_reason_b': dim3_reason_b,
        'field_ta_dim7_score_b': 1,
        'field_ta_dim7_reason_a': dim7_reason_a,
        'field_ta_dim7_reason_b': dim7_reason_b,
        COMPARATIVE_FIELD_ID: comparative_rationale,
        'field_adj_rationale': comparative_rationale
    }

    t_res = await page.evaluate("""async ({ taskId, fields }) => {
        const token = await window.Clerk.session.getToken({ skipCache: true });
        const headers = {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json',
            'x-campaign-id': localStorage.getItem('x-campaign-id') || 'camp_75099d23386f4394ab7596a5ea538da8',
            'x-company-id': localStorage.getItem('x-company-id') || 'comp_2fa4115109d741cd94a3c409ed89e61f',
            'x-account-id': localStorage.getItem('x-account-id') || 'acct_85b680d4c5ba49a29f19c173672aebea'
        };

        const res = await fetch(`https://api.studio.mercor.com/tasks/${taskId}`, {
            method: 'PATCH',
            headers,
            body: JSON.stringify({ custom_fields: fields })
        });
        return { status: res.status, data: await res.json() };
    }""", { 'taskId': TASK_ID, 'fields': patch_fields })
    print("Task custom_fields PATCH status:", t_res['status'], flush=True)

    # 3. Update DOM textareas and inputs so UI stays strictly in sync
    await page.evaluate("""({ compText, d3bText, d7aText, d7bText, compId }) => {
        function setArea(id, val) {
            const el = document.getElementById(id);
            if (el) {
                const proto = window.HTMLTextAreaElement.prototype;
                const desc = Object.getOwnPropertyDescriptor(proto, 'value');
                if (desc && desc.set) desc.set.call(el, val);
                else el.value = val;
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
            }
        }
        setArea(compId, compText);
        setArea('field_adj_rationale', compText);
        setArea('field_ta_dim3_reason_b', d3bText);
        setArea('field_ta_dim7_reason_a', d7aText);
        setArea('field_ta_dim7_reason_b', d7bText);
    }""", {
        'compText': comparative_rationale,
        'd3bText': dim3_reason_b,
        'd7aText': dim7_reason_a,
        'd7bText': dim7_reason_b,
        'compId': COMPARATIVE_FIELD_ID
    })

    await asyncio.sleep(2)

    # 4. Trigger Run AutoQC
    print("Triggering Run AutoQC...", flush=True)
    run_btn = page.locator('button:has-text("Run AutoQC")')
    if await run_btn.count() > 0:
        await run_btn.first.click()
        print("Clicked Run AutoQC successfully!", flush=True)
    else:
        # Fallback click via JS
        clicked = await page.evaluate("""() => {
            const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText && b.innerText.includes('Run AutoQC'));
            if (btn) { btn.click(); return true; }
            return false;
        }""")
        print("JS clicked Run AutoQC:", clicked, flush=True)

    await asyncio.sleep(3)
    await page.screenshot(path='autoqc_triggered.png')
    print("Saved autoqc_triggered.png", flush=True)

    await p.stop()
    print("Fixes applied successfully!", flush=True)

if __name__ == '__main__':
    asyncio.run(apply_fixes())
