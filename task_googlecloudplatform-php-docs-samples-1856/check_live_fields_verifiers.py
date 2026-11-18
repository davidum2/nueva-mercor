import asyncio
import json
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def check_live():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    data = await page.evaluate('''async (taskId) => {
        const token = await window.Clerk.session.getToken({ skipCache: true });
        const headers = {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json',
            'x-campaign-id': localStorage.getItem('x-campaign-id') || 'camp_75099d23386f4394ab7596a5ea538da8',
            'x-company-id': localStorage.getItem('x-company-id') || 'comp_2fa4115109d741cd94a3c409ed89e61f',
            'x-account-id': localStorage.getItem('x-account-id') || 'acct_85b680d4c5ba49a29f19c173672aebea'
        };

        const [tRes, vRes] = await Promise.all([
            fetch(`https://api.studio.mercor.com/tasks/${taskId}`, { headers }).then(r => r.json()),
            fetch(`https://api.studio.mercor.com/verifiers/task/${taskId}`, { headers }).then(r => r.json())
        ]);

        return {
            task_status: tRes.status,
            custom_fields: tRes.custom_fields,
            verifiers: vRes
        };
    }''', TASK_ID)

    cf = data['custom_fields']
    print("=== TASK CUSTOM FIELDS ===")
    print("field_rubric_count:", repr(cf.get('field_rubric_count')))
    
    # Check all rubric keys in custom_fields
    rubric_keys = [k for k in cf if 'rubric' in k]
    print(f"Total rubric keys in cf: {len(rubric_keys)}")
    for k in sorted(rubric_keys):
        val = cf[k]
        val_str = str(val)[:40] if val is not None else 'None'
        print(f"  {k} = {val_str}")

    print("\n=== VERIFIERS ===")
    verifiers = data['verifiers']
    v_list = verifiers if isinstance(verifiers, list) else verifiers.get('verifiers', [])
    print(f"Total verifiers: {len(v_list)}")
    for i, v in enumerate(v_list):
        print(f"[{i}] id={v.get('verifier_id') or v.get('id')} dim={v.get('eval_dimension_id')} crit={repr(v.get('criteria_statement')[:60])}")

    await p.stop()

if __name__ == '__main__':
    asyncio.run(check_live())
