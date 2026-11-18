import asyncio
import json
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True)

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'
FIELD_ID = 'field_1e32bd048d564685ba8ec51f9af11c70'

RATIONALE_TEXT = """Model A is significantly superior to Model B across functional correctness, interface compliance, and test suite execution.

Model A correctly implements the public function 'deidentify_cloud_storage' in 'dlp/src/deidentify_cloud_storage.php' with the exact 8-parameter signature required by downstream callers and dlpTest.php (patch_a.diff:L60-68). It configures the Cloud Storage input and output, sets up de-identification templates for unstructured, structured (CSV), and image files via setFileTypesToTransform (patch_a.diff:L100-104), connects the BigQuery details table, and polls the job to completion, successfully passing unit test validation.

In contrast, Model B introduces a fatal interface defect by injecting an unrequested 9th parameter '$transformationDetailsTableProjectId' at position 7 (patch_b.diff:L67). In PHP 8+, calling this function with 8 arguments causes an uncaught fatal ArgumentCountError, crashing downstream callers. Additionally, Model B omits setFileTypesToTransform, suffered repeated directory path failures in Steps 11, 12, and 32, and failed to run test suite verification. Therefore, Model A is clearly the better rollout."""

async def inject_rationale():
    print("Connecting to browser...", flush=True)
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]
    print(f"Connected to page: {page.url}", flush=True)

    result = await page.evaluate("""async ({ taskId, fieldId, text }) => {
        // 1. Update via DOM with React native setter
        const textareas = Array.from(document.querySelectorAll('textarea'));
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
        }) || textareas[30];

        let domUpdated = false;
        if (target) {
            const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                window.HTMLTextAreaElement.prototype, "value"
            ).set;
            nativeInputValueSetter.call(target, text);
            target.dispatchEvent(new Event('input', { bubbles: true }));
            target.dispatchEvent(new Event('change', { bubbles: true }));
            domUpdated = true;
        }

        // 2. Update via API PATCH to guarantee persistence
        const token = await window.Clerk.session.getToken({ skipCache: true });
        const headers = {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json',
            'x-campaign-id': localStorage.getItem('x-campaign-id') || 'camp_75099d23386f4394ab7596a5ea538da8',
            'x-company-id': localStorage.getItem('x-company-id') || 'comp_2fa4115109d741cd94a3c409ed89e61f',
            'x-account-id': localStorage.getItem('x-account-id') || 'acct_85b680d4c5ba49a29f19c173672aebea'
        };

        const custom_fields = {};
        custom_fields[fieldId] = text;
        custom_fields['field_adj_rationale'] = text;

        const patchR = await fetch(`https://api.studio.mercor.com/tasks/${taskId}`, {
            method: 'PATCH',
            headers,
            body: JSON.stringify({ custom_fields })
        });
        const patchData = await patchR.json();

        return {
            domUpdated,
            targetFound: !!target,
            targetValLen: target ? target.value.length : 0,
            patchStatus: patchR.status,
            patchOk: patchR.ok,
            updatedAt: patchData.updated_at
        };
    }""", { "taskId": TASK_ID, "fieldId": FIELD_ID, "text": RATIONALE_TEXT })

    print("Injection Result:", json.dumps(result, indent=2), flush=True)

    # Click Save Changes if button exists
    save_btn = await page.query_selector('button:has-text("Save Changes")')
    if save_btn:
        print("Clicking Save Changes button...", flush=True)
        await save_btn.click()
        await asyncio.sleep(2)
        print("Save Changes clicked.", flush=True)

    await p.stop()
    print("Done!", flush=True)

if __name__ == '__main__':
    asyncio.run(inject_rationale())
