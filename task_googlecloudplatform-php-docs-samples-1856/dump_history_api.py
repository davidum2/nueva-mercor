import asyncio
import json
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def dump_history():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    hist = await page.evaluate('''async (taskId) => {
        const token = await window.Clerk.session.getToken({ skipCache: true });
        const headers = {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json',
            'x-campaign-id': localStorage.getItem('x-campaign-id') || 'camp_75099d23386f4394ab7596a5ea538da8',
            'x-company-id': localStorage.getItem('x-company-id') || 'comp_2fa4115109d741cd94a3c409ed89e61f',
            'x-account-id': localStorage.getItem('x-account-id') || 'acct_85b680d4c5ba49a29f19c173672aebea'
        };

        const res = await fetch(`https://api.studio.mercor.com/tasks/${taskId}/history`, { headers });
        return await res.json();
    }''', TASK_ID)

    items = hist.get('history', [])
    print(f"Total history items: {len(items)}")
    for i, item in enumerate(items):
        print(f"=== ITEM {i} ===")
        print(f"Status: {item.get('status')} | Transitioned by: {item.get('transitioned_by')} | Edge: {item.get('edge_id')} | Created at: {item.get('created_at')}")
        if item.get('notes') or item.get('feedback') or item.get('reason') or item.get('review_feedback'):
            print("  Notes/Feedback:", item.get('notes') or item.get('feedback') or item.get('reason') or item.get('review_feedback'))
        # check all keys of item
        for k, v in item.items():
            if k not in ['status', 'transitioned_by', 'edge_id', 'created_at', 'task_id', 'id'] and v:
                print(f"  {k}: {str(v)[:300]}")

    await p.stop()

if __name__ == '__main__':
    asyncio.run(dump_history())
