import asyncio
import json
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def get_dimensions():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    dim_data = await page.evaluate("""async (taskId) => {
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
        
        return task.custom_fields;
    }""", TASK_ID)

    # Filter to dimension fields
    dim_fields = {}
    for k, v in dim_data.items():
        if 'dim' in k or 'score' in k or 'rationale' in k or '1e32' in k or 'e511' in k:
            dim_fields[k] = v

    print(json.dumps(dim_fields, indent=2))

    await p.stop()

if __name__ == '__main__':
    asyncio.run(get_dimensions())
