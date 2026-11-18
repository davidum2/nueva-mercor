import asyncio
import json
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'
VERIFIER_13_ID = 'ver_c1edf3d7330449e1b351286330f42ebb'
PAIRWISE_FIELD_ID = 'field_e511999a150a45c2b7145f808103d78c'

async def set_inputs():
    print("Connecting to browser...", flush=True)
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    # 1. Set Pairwise Evaluation to 'A MUCH BETTER' in UI
    tie_btn = page.locator('button[role="combobox"]').filter(has_text="TIE").or_(
        page.locator('button[role="combobox"]').filter(has_text="A BETTER")
    )
    if await tie_btn.count() > 0:
        print("Clicking Pairwise combobox...", flush=True)
        await tie_btn.first.click()
        await asyncio.sleep(1)
        # Click option 'A MUCH BETTER'
        opt_much = page.locator('[role="option"]:has-text("A MUCH BETTER")')
        if await opt_much.count() > 0:
            await opt_much.first.click()
            print("Selected 'A MUCH BETTER' successfully!", flush=True)
        else:
            print("Option 'A MUCH BETTER' not found.", flush=True)
        await asyncio.sleep(1)

    # 2. Set Rubric count to '12' in UI
    count_btn = page.locator('button[role="combobox"]').filter(has_text="13")
    if await count_btn.count() > 0:
        print("Clicking Rubric count combobox...", flush=True)
        await count_btn.first.click()
        await asyncio.sleep(1)
        opt_12 = page.locator('[role="option"]:has-text("12")')
        if await opt_12.count() > 0:
            await opt_12.first.click()
            print("Selected Rubric count '12' successfully!", flush=True)
        else:
            print("Option '12' not found.", flush=True)
        await asyncio.sleep(1)

    # 3. Delete Verifier 13 and PATCH task custom fields via API
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

        // PATCH task
        const custom_fields = {
            field_rubric_count: "12",
            [pwField]: "A_MUCH_BETTER"
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
    print("API update:", json.dumps(api_res, indent=2), flush=True)

    # 4. Click Save Changes button
    save_btn = await page.query_selector('button:has-text("Save Changes")')
    if save_btn:
        print("Clicking Save Changes...", flush=True)
        await save_btn.click()
        await asyncio.sleep(2)

    # 5. Trigger Run AutoQC
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

    await page.screenshot(path='set_inputs_finished.png')
    print("Saved set_inputs_finished.png", flush=True)

    await p.stop()
    print("Done!", flush=True)

if __name__ == '__main__':
    asyncio.run(set_inputs())
