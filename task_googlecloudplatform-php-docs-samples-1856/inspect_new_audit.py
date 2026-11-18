import asyncio
import json
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def inspect_latest():
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

        const res = await fetch(`https://api.studio.mercor.com/qc-audits/?subject_kind=task&subject_id=${taskId}&limit=5`, { headers });
        const data = await res.json();
        const list = data.audits || (Array.isArray(data) ? data : []);
        const latest = list[0];

        const fullRes = await fetch(`https://api.studio.mercor.com/qc-audits/${latest.id || latest.qc_audit_id}`, { headers });
        const fullAudit = await fullRes.json();

        return fullAudit;
    }''', TASK_ID)

    print("=== LATEST AUTOQC AUDIT (JUST FINISHED) ===")
    print("ID:", data.get('qc_audit_id'))
    print("Created at:", data.get('created_at'))
    print("Verdict:", data.get('verdict'))
    print("Status:", data.get('status'))

    sections = data.get('outcome', {}).get('sections', [])
    for s in sections:
        for d in s.get('dimensions', []):
            if d.get('status') == 'fail' or d.get('findings'):
                print(f"\n[{d.get('dim_id')}] {d.get('dimension')} --> {d.get('status')}")
                findings = d.get('findings') or []
                print("  Summary:", d.get('summary'))
                for f in findings:
                    print(f"  * {f.get('title')} [{f.get('severity')}]: {f.get('description')}")
                    if f.get('suggested_fix'):
                        print(f"    Fix: {f.get('suggested_fix')}")

    await p.stop()

if __name__ == '__main__':
    asyncio.run(inspect_latest())
