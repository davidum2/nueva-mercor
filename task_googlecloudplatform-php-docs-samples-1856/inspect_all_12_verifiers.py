import asyncio
import json
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def get_verifiers():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    v_data = await page.evaluate("""async (taskId) => {
        const token = await window.Clerk.session.getToken({ skipCache: true });
        const headers = {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json',
            'x-campaign-id': localStorage.getItem('x-campaign-id') || 'camp_75099d23386f4394ab7596a5ea538da8',
            'x-company-id': localStorage.getItem('x-company-id') || 'comp_2fa4115109d741cd94a3c409ed89e61f',
            'x-account-id': localStorage.getItem('x-account-id') || 'acct_85b680d4c5ba49a29f19c173672aebea'
        };

        const res = await fetch(`https://api.studio.mercor.com/verifiers/task/${taskId}`, { headers });
        return await res.json();
    }""", TASK_ID)

    items = v_data if isinstance(v_data, list) else v_data.get('verifiers', [])
    print(f"Total verifiers: {len(items)}")
    for v in sorted(items, key=lambda x: x.get('verifier_index', 0)):
        idx = v.get('verifier_index')
        vid = v.get('verifier_id')
        crit = v.get('verifier_values', {}).get('criteria')
        cf = v.get('verifier_custom_field_values', {})
        ans_a = cf.get('answer_a')
        ans_b = cf.get('answer_b')
        dim = cf.get('mapped_dimension')
        print(f"[{idx}] {vid}: A={ans_a}, B={ans_b} | {dim} | {crit}")

    await p.stop()

if __name__ == '__main__':
    asyncio.run(get_verifiers())
