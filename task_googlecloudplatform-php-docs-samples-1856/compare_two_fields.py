import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def check_texts():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url][0]

    cf = await page.evaluate('''async (taskId) => {
        const token = await window.Clerk.session.getToken({ skipCache: true });
        const headers = {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json',
            'x-campaign-id': localStorage.getItem('x-campaign-id') || 'camp_75099d23386f4394ab7596a5ea538da8',
            'x-company-id': localStorage.getItem('x-company-id') || 'comp_2fa4115109d741cd94a3c409ed89e61f',
            'x-account-id': localStorage.getItem('x-account-id') || 'acct_85b680d4c5ba49a29f19c173672aebea'
        };

        const res = await fetch(`https://api.studio.mercor.com/tasks/${taskId}`, { headers });
        const task = await res.json();
        const custom = task.custom_fields || {};
        return {
            field_comp: custom['field_1e32bd048d564685ba8ec51f9af11c70'],
            field_adj: custom['field_adj_rationale']
        };
    }''', TASK_ID)

    is_identical = cf['field_comp'] == cf['field_adj']
    print(f"Are field_1e32bd048d564685ba8ec51f9af11c70 and field_adj_rationale identical? {is_identical}")
    print("field_adj length:", len(cf['field_adj'] or ''))
    print("field_comp length:", len(cf['field_comp'] or ''))

    await p.stop()

if __name__ == '__main__':
    asyncio.run(check_texts())
