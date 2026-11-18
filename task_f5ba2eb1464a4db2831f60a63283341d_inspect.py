import asyncio
import json
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_f5ba2eb1464a4db2831f60a63283341d'
TASK_URL = f'https://studio.mercor.com/annotator/tasks/{TASK_ID}/?from_view=3706ca8d-1ee2-4855-ad54-f952afd4a7be&campaignId=camp_75099d23386f4394ab7596a5ea538da8'
OUT_DIR = os.path.join(os.getcwd(), f'task_{TASK_ID}')
os.makedirs(OUT_DIR, exist_ok=True)

async def inspect_new_task():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    ctx = browser.contexts[0]
    
    # Check if page is already open
    target_page = None
    for pg in ctx.pages:
        if TASK_ID in pg.url:
            target_page = pg
            break
            
    if not target_page:
        print(f"Task page not open yet. Navigating active page or opening new tab...")
        # Use an existing mercor page if available, else new page
        mercor_pages = [pg for pg in ctx.pages if 'mercor.com' in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
        if mercor_pages:
            target_page = mercor_pages[0]
            print(f"Navigating page {target_page.url} to {TASK_URL}")
            await target_page.goto(TASK_URL, wait_until='domcontentloaded')
        else:
            target_page = await ctx.new_page()
            await target_page.goto(TASK_URL, wait_until='domcontentloaded')

    print("Waiting 5s for page to initialize...", flush=True)
    await asyncio.sleep(5)

    # Fetch token and basic IDs
    api_data = await target_page.evaluate('''async (taskId) => {
        const token = await window.Clerk.session.getToken({ skipCache: true });
        const headers = {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json',
            'x-campaign-id': localStorage.getItem('x-campaign-id') || 'camp_75099d23386f4394ab7596a5ea538da8',
            'x-company-id': localStorage.getItem('x-company-id') || 'comp_2fa4115109d741cd94a3c409ed89e61f',
            'x-account-id': localStorage.getItem('x-account-id') || 'acct_85b680d4c5ba49a29f19c173672aebea'
        };

        // 1. Task details
        const taskRes = await fetch(`https://api.studio.mercor.com/tasks/${taskId}`, { headers });
        const taskData = await taskRes.json();

        // 2. Task history
        const histRes = await fetch(`https://api.studio.mercor.com/tasks/${taskId}/history`, { headers });
        const histData = await histRes.json();

        // 3. Verifiers
        const verRes = await fetch(`https://api.studio.mercor.com/verifiers/task/${taskId}`, { headers });
        const verData = await verRes.json();

        // 4. QC Audits
        const qcRes = await fetch(`https://api.studio.mercor.com/qc-audits/?subject_kind=task&subject_id=${taskId}&limit=20`, { headers });
        const qcData = await qcRes.json();

        return {
            task: taskData,
            history: histData,
            verifiers: verData,
            qcAudits: qcData
        };
    }''', TASK_ID)

    # Save to disk
    with open(os.path.join(OUT_DIR, 'task_api.json'), 'w', encoding='utf-8') as f:
        json.dump(api_data['task'], f, indent=2)

    with open(os.path.join(OUT_DIR, 'history_api.json'), 'w', encoding='utf-8') as f:
        json.dump(api_data['history'], f, indent=2)

    with open(os.path.join(OUT_DIR, 'verifiers_api.json'), 'w', encoding='utf-8') as f:
        json.dump(api_data['verifiers'], f, indent=2)

    with open(os.path.join(OUT_DIR, 'qc_audits_api.json'), 'w', encoding='utf-8') as f:
        json.dump(api_data['qcAudits'], f, indent=2)

    task_obj = api_data['task']
    print(f"=== TASK METADATA ===")
    print(f"Task ID: {task_obj.get('id') or task_obj.get('task_id')}")
    print(f"Title / Name: {task_obj.get('name')}")
    print(f"Status: {task_obj.get('status')} | State: {task_obj.get('state')}")
    print(f"Assigned User: {task_obj.get('assigned_user_id')}")
    print(f"Template ID: {task_obj.get('template_id')}")
    print(f"Created: {task_obj.get('created_at')} | Updated: {task_obj.get('updated_at')}")

    # History summary
    history = api_data['history']
    hist_items = history if isinstance(history, list) else history.get('history', history.get('items', []))
    print(f"\n=== HISTORY EVENTS ({len(hist_items)}) ===")
    for h in hist_items[:15]:
        action = h.get('action') or h.get('event') or h.get('type')
        user = h.get('user_id') or h.get('actor') or h.get('created_by')
        ts = h.get('created_at') or h.get('timestamp')
        print(f"[{ts}] {action} by {user}")
        if h.get('comment') or h.get('notes') or h.get('feedback'):
            print(f"   Comment: {h.get('comment') or h.get('notes') or h.get('feedback')}")

    # Take screenshot
    ss_path = os.path.join(OUT_DIR, 'initial_task_screen.png')
    await target_page.screenshot(path=ss_path)
    print(f"\nSaved initial screenshot to {ss_path}")

    await p.stop()

if __name__ == '__main__':
    asyncio.run(inspect_new_task())
