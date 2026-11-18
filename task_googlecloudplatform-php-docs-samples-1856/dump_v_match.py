import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def dump():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    verifiers = await page.evaluate('''async (taskId) => {
        const token = await window.Clerk.session.getToken({ skipCache: true });
        const headers = {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json',
            'x-campaign-id': localStorage.getItem('x-campaign-id') || 'camp_75099d23386f4394ab7596a5ea538da8',
            'x-company-id': localStorage.getItem('x-company-id') || 'comp_2fa4115109d741cd94a3c409ed89e61f',
            'x-account-id': localStorage.getItem('x-account-id') || 'acct_85b680d4c5ba49a29f19c173672aebea'
        };

        const res = await fetch(`https://api.studio.mercor.com/verifiers/task/${taskId}`, { headers });
        const list = await res.json();
        return (list.verifiers || list).map(v => ({
            id: v.verifier_id,
            index: v.verifier_index,
            criteria: v.verifier_values ? v.verifier_values.criteria : '',
            reason_a: v.verifier_custom_field_values ? v.verifier_custom_field_values.reason_a : '',
            reason_b: v.verifier_custom_field_values ? v.verifier_custom_field_values.reason_b : ''
        }));
    }''', TASK_ID)

    for v in sorted(verifiers, key=lambda x: x['index']):
        idx = v['index']
        ra = v['reason_a'] or ''
        rb = v['reason_b'] or ''
        print(f"Verifier [{idx}] ({v['id']}):")
        print("  Reason A:", ra)
        print("  Reason B:", rb)
        print()

    await p.stop()

if __name__ == '__main__':
    asyncio.run(dump())
