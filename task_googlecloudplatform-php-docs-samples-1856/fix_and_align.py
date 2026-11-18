import asyncio
import json
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'
VERIFIER_13_ID = 'ver_c1edf3d7330449e1b351286330f42ebb'
PAIRWISE_FIELD_ID = 'field_e511999a150a45c2b7145f808103d78c'

async def fix_and_align():
    print("Connecting to browser...", flush=True)
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    # 1. Select 'A MUCH BETTER' in the UI dropdown
    # Find button displaying current pairwise verdict ('TIE', 'A BETTER', etc.)
    pw_trigger = page.locator('div:has-text("PAIRWISE VERDICT") button').first
    if await pw_trigger.count() > 0:
        await pw_trigger.click()
        await asyncio.sleep(1)
        opt = page.locator('[role="option"]:has-text("A MUCH BETTER")').first
        if await opt.count() > 0:
            await opt.click()
            print("Selected 'A MUCH BETTER' in UI dropdown!", flush=True)
        else:
            print("Option 'A MUCH BETTER' not found in dropdown.", flush=True)

    # 2. Delete Rubric 13 via API and set rubric count to 12
    api_res = await page.evaluate("""async ({ taskId, ver13Id, pwField }) => {
        const token = await window.Clerk.session.getToken({ skipCache: true });
        const headers = {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json',
            'x-campaign-id': localStorage.getItem('x-campaign-id') || 'camp_75099d23386f4394ab7596a5ea538da8',
            'x-company-id': localStorage.getItem('x-company-id') || 'comp_2fa4115109d741cd94a3c409ed89e61f',
            'x-account-id': localStorage.getItem('x-account-id') || 'acct_85b680d4c5ba49a29f19c173672aebea'
        };

        // DELETE Verifier 13
        const delR = await fetch(`https://api.studio.mercor.com/verifiers/${ver13Id}`, {
            method: 'DELETE',
            headers
        });

        // PATCH task custom fields: rubric count = 12, pairwise = A_MUCH_BETTER, clear rubric 13 fields
        const custom_fields = {
            field_rubric_count: "12",
            [pwField]: "A_MUCH_BETTER",
            field_ta_rubric_13_answer_a: null,
            field_ta_rubric_13_reason_a: null,
            field_ta_rubric_13_mapped_dimension_a: null,
            field_ta_rubric_13_answer_b: null,
            field_ta_rubric_13_reason_b: null,
            field_ta_rubric_13_mapped_dimension_b: null
        };

        const patchR = await fetch(`https://api.studio.mercor.com/tasks/${taskId}`, {
            method: 'PATCH',
            headers,
            body: JSON.stringify({ custom_fields })
        });
        const patchData = await patchR.json();

        return {
            deleteStatus: delR.status,
            patchStatus: patchR.status,
            updatedAt: patchData.updated_at
        };
    }""", { 'taskId': TASK_ID, 'ver13Id': VERIFIER_13_ID, 'pwField': PAIRWISE_FIELD_ID })

    print("API update result:", json.dumps(api_res, indent=2), flush=True)

    # 3. Click Save Changes button
    save_btn = await page.query_selector('button:has-text("Save Changes")')
    if save_btn:
        print("Clicking Save Changes...", flush=True)
        await save_btn.click()
        await asyncio.sleep(2)

    # 4. Trigger Run AutoQC
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
    print("AutoQC trigger result:", run_res, flush=True)

    await page.screenshot(path='after_fix_and_align.png')
    print("Saved after_fix_and_align.png")
    await p.stop()

if __name__ == '__main__':
    asyncio.run(fix_and_align())
