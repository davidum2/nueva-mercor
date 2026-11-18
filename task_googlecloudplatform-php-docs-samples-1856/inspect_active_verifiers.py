import asyncio
import json
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def check_v():
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

        const res = await fetch(`https://api.studio.mercor.com/verifiers/task/${taskId}`, { headers });
        const verifiers = await res.json();
        const taskRes = await fetch(`https://api.studio.mercor.com/tasks/${taskId}`, { headers });
        const task = await taskRes.json();

        return {
            verifiers: verifiers.verifiers || verifiers,
            custom_fields: task.custom_fields
        };
    }''', TASK_ID)

    print('=== VERIFIERS ===')
    v_list = data['verifiers'] if isinstance(data['verifiers'], list) else []
    for i, v in enumerate(v_list):
        print(f'[{i}] ID: {v.get("verifier_id") or v.get("id")}')
        print(f'    Dim: {v.get("eval_dimension_id")}')
        crit = v.get("criteria_statement") or v.get("config_input", {}).get("criteria")
        print(f'    Crit: {crit}')

    print('\n=== RUBRIC CUSTOM FIELDS (1 to 9) ===')
    cf = data['custom_fields']
    for i in range(1, 10):
        si = f'{i:02d}'
        print(f'Rubric {si}:')
        print(f'  ans_a: {cf.get(f"field_ta_rubric_{si}_answer_a")}, ans_b: {cf.get(f"field_ta_rubric_{si}_answer_b")}')
        print(f'  dim_a: {cf.get(f"field_ta_rubric_{si}_mapped_dimension_a")}')
        ra = cf.get(f"field_ta_rubric_{si}_reason_a") or ''
        rb = cf.get(f"field_ta_rubric_{si}_reason_b") or ''
        print(f'  reason_a: {ra[:120]}...')
        print(f'  reason_b: {rb[:120]}...')

    await p.stop()

if __name__ == '__main__':
    asyncio.run(check_v())
