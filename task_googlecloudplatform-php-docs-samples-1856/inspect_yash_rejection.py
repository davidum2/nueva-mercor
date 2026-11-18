import asyncio
import sys
import json
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def inspect_history():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    res = await page.evaluate('''async (taskId) => {
        const token = await window.Clerk.session.getToken({ skipCache: true });
        const headers = {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json',
            'x-campaign-id': localStorage.getItem('x-campaign-id') || 'camp_75099d23386f4394ab7596a5ea538da8',
            'x-company-id': localStorage.getItem('x-company-id') || 'comp_2fa4115109d741cd94a3c409ed89e61f',
            'x-account-id': localStorage.getItem('x-account-id') || 'acct_85b680d4c5ba49a29f19c173672aebea'
        };

        // Try various history/events endpoints
        const endpoints = [
            `https://api.studio.mercor.com/tasks/${taskId}`,
            `https://api.studio.mercor.com/tasks/${taskId}/transitions`,
            `https://api.studio.mercor.com/tasks/${taskId}/history`,
            `https://api.studio.mercor.com/task-transitions/?task_id=${taskId}`,
            `https://api.studio.mercor.com/task-events/?task_id=${taskId}`,
            `https://api.studio.mercor.com/reviews/?task_id=${taskId}`,
            `https://api.studio.mercor.com/qc-audits/?subject_kind=task&subject_id=${taskId}`
        ];

        const results = {};
        for (const ep of endpoints) {
            try {
                const r = await fetch(ep, { headers });
                results[ep] = { status: r.status, data: r.ok ? await r.json() : null };
            } catch(e) {
                results[ep] = { error: e.message };
            }
        }

        // Also extract the HISTORY table directly from the DOM
        const rows = Array.from(document.querySelectorAll('tr')).map(r => {
            const cells = Array.from(r.querySelectorAll('th, td')).map(c => c.innerText.trim());
            return cells;
        });

        return { results, tableRows: rows };
    }''', TASK_ID)

    print("=== HISTORY TABLE FROM DOM ===")
    for r in res.get('tableRows', []):
        print("ROW:", " | ".join(r))

    print("\n=== ENDPOINT RESULTS ===")
    for ep, data in res.get('results', {}).items():
        print(f"\n--- {ep} (Status: {data.get('status')}) ---")
        if data.get('data'):
            d = data['data']
            if isinstance(d, list):
                print(f"List with {len(d)} items:")
                for item in d[:5]:
                    print(" ", json.dumps(item)[:200])
            elif isinstance(d, dict):
                keys = list(d.keys())
                print(f"Dict with keys: {keys}")
                for k in keys:
                    v = d[k]
                    if isinstance(v, list):
                        print(f"  {k}: list with {len(v)} items")
                    elif isinstance(v, (dict, str, int, bool)) and v is not None:
                        s = str(v)
                        if len(s) < 200:
                            print(f"  {k}: {s}")

    await p.stop()

if __name__ == '__main__':
    asyncio.run(inspect_history())
