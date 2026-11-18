import asyncio
import sys
import json
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def check_recent_audits():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url][0]

    res = await page.evaluate('''async (taskId) => {
        const token = await window.Clerk.session.getToken({ skipCache: true });
        const headers = {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json',
            'x-campaign-id': localStorage.getItem('x-campaign-id') || 'camp_75099d23386f4394ab7596a5ea538da8',
            'x-company-id': localStorage.getItem('x-company-id') || 'comp_2fa4115109d741cd94a3c409ed89e61f',
            'x-account-id': localStorage.getItem('x-account-id') || 'acct_85b680d4c5ba49a29f19c173672aebea'
        };

        const res = await fetch(`https://api.studio.mercor.com/qc-audits/?subject_kind=task&subject_id=${taskId}&limit=100`, { headers });
        const data = await res.json();
        const audits = data.audits || (Array.isArray(data) ? data : []);
        const sorted = audits.toSorted((a,b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());

        return sorted.slice(0, 8).map(a => ({
            id: a.id || a.qc_audit_id,
            created_at: a.created_at,
            created_by: a.created_by,
            status: a.status,
            findings: (a.findings || []).map(f => ({
                title: f.title,
                severity: f.severity,
                desc: f.description,
                suggested_fix: f.suggested_fix
            }))
        }));
    }''', TASK_ID)

    for a in res:
        print(f"=== AUDIT {a['id']} ({a['created_at']}) by {a['created_by']} ===")
        print(f"Findings count: {len(a['findings'])}")
        for f in a['findings']:
            print(f"  [{f['severity']}] {f['title']}")
            print(f"    Desc: {f['desc'][:300]}")
            if f.get('suggested_fix'):
                print(f"    Fix: {f['suggested_fix'][:300]}")

    await p.stop()

if __name__ == '__main__':
    asyncio.run(check_recent_audits())
