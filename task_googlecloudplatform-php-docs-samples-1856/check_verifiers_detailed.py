import asyncio
import json
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def check_all_v():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]
    
    data = await page.evaluate("""async ({ taskId }) => {
        const token = await window.Clerk.session.getToken({ skipCache: true });
        const headers = {
            'Authorization': 'Bearer ' + token,
            'x-campaign-id': localStorage.getItem('x-campaign-id') || 'camp_75099d23386f4394ab7596a5ea538da8',
            'x-company-id': localStorage.getItem('x-company-id') || 'comp_2fa4115109d741cd94a3c409ed89e61f',
            'x-account-id': localStorage.getItem('x-account-id') || 'acct_85b680d4c5ba49a29f19c173672aebea'
        };
        const r = await fetch(`https://api.studio.mercor.com/verifiers/task/${taskId}`, { headers });
        const d = await r.json();
        return (d.verifiers || []).map(v => ({
            id: v.verifier_id,
            idx: v.verifier_index,
            crit: v.verifier_values ? v.verifier_values.criteria : '',
            cf: v.verifier_custom_field_values || {}
        }));
    }""", { 'taskId': TASK_ID })
    
    print(f"Total verifiers: {len(data)}")
    for v in sorted(data, key=lambda x: x['idx'] if x['idx'] is not None else 99):
        cf = v['cf']
        ans_a = cf.get('answer_a')
        ans_b = cf.get('answer_b')
        ra = len(cf.get('reason_a') or '')
        rb = len(cf.get('reason_b') or '')
        src = cf.get('rubric_source')
        dim = cf.get('mapped_dimension')
        print(f"  [{v['idx']:02d}] id={v['id']} | A={ans_a} (len={ra}) | B={ans_b} (len={rb}) | src={src} | dim={dim}")
        
    await p.stop()

if __name__ == '__main__':
    asyncio.run(check_all_v())
