import asyncio
import json
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_08ccf272669347c3af63de71b2ecb5e5'
CAMPAIGN_ID = 'camp_75099d23386f4394ab7596a5ea538da8'
FROM_VIEW = '3706ca8d-1ee2-4855-ad54-f952afd4a7be'
TARGET_URL = f"https://studio.mercor.com/annotator/tasks/{TASK_ID}/?from_view={FROM_VIEW}&campaignId={CAMPAIGN_ID}"

TASK_DIR = os.path.join(r'c:\desarrollo\nueva-mercor', f'task_{TASK_ID}')
os.makedirs(TASK_DIR, exist_ok=True)

async def inspect():
    p = await async_playwright().start()
    b = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')

    # Find mercor page or navigate
    mercor_pages = [pg for pg in b.contexts[0].pages if 'studio.mercor.com' in pg.url]
    if mercor_pages:
        page = mercor_pages[0]
        print(f"Navigating existing page from {page.url} to {TARGET_URL}...")
        await page.goto(TARGET_URL, wait_until='domcontentloaded')
    else:
        print("Creating new page...")
        page = await b.contexts[0].new_page()
        await page.goto(TARGET_URL, wait_until='domcontentloaded')

    await asyncio.sleep(6)
    print("Page Title:", await page.title())
    print("Page URL:", page.url)

    # Screenshot initial screen
    ss_initial = os.path.join(TASK_DIR, 'initial_screen.png')
    await page.screenshot(path=ss_initial)
    print(f"Saved {ss_initial}")

    # Fetch API data via Clerk credentials
    api_data = await page.evaluate('''async (taskId) => {
        const token = await window.Clerk.session.getToken({ skipCache: true });
        const headers = {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json',
            'x-campaign-id': localStorage.getItem('x-campaign-id') || 'camp_75099d23386f4394ab7596a5ea538da8',
            'x-company-id': localStorage.getItem('x-company-id') || 'comp_2fa4115109d741cd94a3c409ed89e61f',
            'x-account-id': localStorage.getItem('x-account-id') || 'acct_85b680d4c5ba49a29f19c173672aebea'
        };

        const tRes = await fetch(`https://api.studio.mercor.com/tasks/${taskId}`, { headers });
        const task = await tRes.json();

        const vRes = await fetch(`https://api.studio.mercor.com/verifiers/task/${taskId}`, { headers });
        const verifiers = await vRes.json();

        return {
            task,
            verifiers
        };
    }''', TASK_ID)

    task_obj = api_data['task']
    verifiers_obj = api_data['verifiers']

    with open(os.path.join(TASK_DIR, 'task_api.json'), 'w', encoding='utf-8') as f:
        json.dump(task_obj, f, indent=2, ensure_ascii=False)

    with open(os.path.join(TASK_DIR, 'verifiers_api.json'), 'w', encoding='utf-8') as f:
        json.dump(verifiers_obj, f, indent=2, ensure_ascii=False)

    print(f"Saved task_api.json ({len(str(task_obj))} chars)")
    print(f"Saved verifiers_api.json ({len(str(verifiers_obj))} chars)")

    # Print summary of task
    print("\n=== TASK BASIC INFO ===")
    print("Name:", task_obj.get('name'))
    print("Status:", task_obj.get('status'))
    print("Assigned To:", task_obj.get('assigned_to'))
    print("Claimed By:", task_obj.get('claimed_by'))
    print("Current Stage:", task_obj.get('current_stage'))

    cf = task_obj.get('custom_fields', {})
    print("\n=== CUSTOM FIELDS SUMMARY ===")
    print("Task Type:", cf.get('field_task_type'))
    print("Rubric Count:", cf.get('field_rubric_count'))
    print("Quality Score A:", cf.get('field_ta_final_quality_score_a'))
    print("Quality Score B:", cf.get('field_ta_final_quality_score_b'))
    print("Pref Label:", cf.get('field_e511999a150a45c2b7145f808103d78c'))
    print("Adjudication Rationale:", str(cf.get('field_adj_rationale'))[:200])

    await b.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(inspect())
