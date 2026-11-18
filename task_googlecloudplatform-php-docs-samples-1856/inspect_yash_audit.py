import asyncio
import sys
import json
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'
AUDIT_ID = 'qcaud_077fe5aa73593e83427cf509'

async def check():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url][0]

    data = await page.evaluate('''async (auditId) => {
        const token = await window.Clerk.session.getToken({ skipCache: true });
        const headers = {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json',
            'x-campaign-id': localStorage.getItem('x-campaign-id') || 'camp_75099d23386f4394ab7596a5ea538da8',
            'x-company-id': localStorage.getItem('x-company-id') || 'comp_2fa4115109d741cd94a3c409ed89e61f',
            'x-account-id': localStorage.getItem('x-account-id') || 'acct_85b680d4c5ba49a29f19c173672aebea'
        };

        const res = await fetch(`https://api.studio.mercor.com/qc-audits/${auditId}`, { headers });
        return await res.json();
    }''', AUDIT_ID)

    print("=== AUDIT RUN BY YASH S ===")
    print("Verdict:", data.get('verdict'))
    print("Global pass:", data.get('global_pass'))
    print("Status counts:", data.get('status_counts'))
    print("Findings in audit:", data.get('findings'))

    for sec in data.get('outcome', {}).get('sections', []):
        for dim in sec.get('dimensions', []):
            if dim.get('status') == 'fail':
                print(f"FAILED DIMENSION: {dim.get('dimension')} ({dim.get('dim_id')})")
                print("  Findings:", json.dumps(dim.get('findings'), indent=2))
                print("  Votes:", json.dumps(dim.get('votes'), indent=2))

    await p.stop()

if __name__ == '__main__':
    asyncio.run(check())
