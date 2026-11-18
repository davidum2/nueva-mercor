import asyncio
import json
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'
AUDIT_ID = 'qcaud_e20092c05c42a0ae6ee1cdba'

async def dump_audit_findings():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    audit = await page.evaluate('''async ({ auditId }) => {
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
    }''', { 'auditId': AUDIT_ID })

    # Also save full raw audit JSON for offline inspection
    with open('task_googlecloudplatform-php-docs-samples-1856/tyler_audit_full.json', 'w', encoding='utf-8') as f:
        json.dump(audit, f, indent=2)

    print(f"=== FULL FINDINGS FOR AUDIT {AUDIT_ID} ===")
    print(f"Created: {audit.get('created_at')} by {audit.get('created_by')}")
    print(f"Overall verdict: {audit.get('verdict')} | status: {audit.get('status')}")

    sections = audit.get('outcome', {}).get('sections', [])
    for sec in sections:
        sec_title = sec.get('section') or sec.get('title')
        for dim in sec.get('dimensions', []):
            if dim.get('status') == 'fail' or dim.get('findings'):
                print(f"\n=======================================================")
                print(f"DIMENSION: [{dim.get('dim_id')}] {dim.get('dimension')} (Status: {dim.get('status')})")
                print(f"Summary: {dim.get('summary')}")
                findings = dim.get('findings') or []
                for idx, f in enumerate(findings):
                    print(f"\n  --- Finding #{idx+1}: {f.get('title')} [{f.get('severity')}] ---")
                    print(f"  Description: {f.get('description')}")
                    if f.get('evidence'):
                        print(f"  Evidence: {f.get('evidence')}")
                    if f.get('suggested_fix'):
                        print(f"  Suggested Fix: {f.get('suggested_fix')}")

    await p.stop()

if __name__ == '__main__':
    asyncio.run(dump_audit_findings())
