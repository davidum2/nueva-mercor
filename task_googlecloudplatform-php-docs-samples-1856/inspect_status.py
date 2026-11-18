import asyncio
import json
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def check_status():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    if not task_pages:
        print("No task page found!")
        await p.stop()
        return
    page = task_pages[0]

    # Get state from page
    state = await page.evaluate("""async (taskId) => {
        const token = await window.Clerk.session.getToken({ skipCache: true });
        const headers = {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json',
            'x-campaign-id': localStorage.getItem('x-campaign-id') || 'camp_75099d23386f4394ab7596a5ea538da8',
            'x-company-id': localStorage.getItem('x-company-id') || 'comp_2fa4115109d741cd94a3c409ed89e61f',
            'x-account-id': localStorage.getItem('x-account-id') || 'acct_85b680d4c5ba49a29f19c173672aebea'
        };

        // Fetch verifiers
        const vRes = await fetch(`https://api.studio.mercor.com/verifiers/task/${taskId}`, { headers });
        const verifiers = await vRes.json();

        // Fetch task
        const tRes = await fetch(`https://api.studio.mercor.com/tasks/${taskId}`, { headers });
        const task = await tRes.json();

        // Check buttons on page
        const buttons = Array.from(document.querySelectorAll('button')).map(b => ({
            text: b.innerText ? b.innerText.trim() : '',
            disabled: b.disabled,
            ariaDisabled: b.getAttribute('aria-disabled')
        })).filter(b => b.text.length > 0);

        return {
            verifiersCount: Array.isArray(verifiers) ? verifiers.length : verifiers,
            pairwiseField: task.custom_fields ? task.custom_fields['field_e511999a150a45c2b7145f808103d78c'] : null,
            rubricCountField: task.custom_fields ? task.custom_fields['field_rubric_count'] : null,
            autoqcStatus: task.custom_fields ? task.custom_fields['autoqc_status'] : null,
            buttons: buttons.filter(b => b.text.includes('AutoQC') || b.text.includes('Save') || b.text.includes('Submit'))
        };
    }""", TASK_ID)

    print("Current State:", json.dumps(state, indent=2))

    # Click Run AutoQC if present and not running
    run_btn = page.locator('button:has-text("Run AutoQC")')
    if await run_btn.count() > 0:
        is_disabled = await run_btn.first.is_disabled()
        print(f"Run AutoQC button found, disabled={is_disabled}")
        if not is_disabled:
            print("Clicking Run AutoQC...")
            await run_btn.first.click()
            print("Clicked Run AutoQC!")
            await asyncio.sleep(3)
    else:
        print("Run AutoQC button not found directly.")

    await page.screenshot(path='current_mercor_state.png')
    print("Screenshot saved to current_mercor_state.png")

    await p.stop()

if __name__ == '__main__':
    asyncio.run(check_status())
