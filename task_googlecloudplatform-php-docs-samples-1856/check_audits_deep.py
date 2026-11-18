import asyncio
import json
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def check_audits_deep():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    audits = await page.evaluate('''async (taskId) => {
        const token = await window.Clerk.session.getToken({ skipCache: true });
        const headers = {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json',
            'x-campaign-id': localStorage.getItem('x-campaign-id') || 'camp_75099d23386f4394ab7596a5ea538da8',
            'x-company-id': localStorage.getItem('x-company-id') || 'comp_2fa4115109d741cd94a3c409ed89e61f',
            'x-account-id': localStorage.getItem('x-account-id') || 'acct_85b680d4c5ba49a29f19c173672aebea'
        };

        const res = await fetch(`https://api.studio.mercor.com/qc-audits/?subject_kind=task&subject_id=${taskId}&limit=20`, { headers });
        const data = await res.json();
        const list = data.audits || (Array.isArray(data) ? data : []);

        const details = [];
        for (const a of list.slice(0, 8)) {
            const r = await fetch(`https://api.studio.mercor.com/qc-audits/${a.id || a.qc_audit_id}`, { headers });
            details.push(await r.json());
        }
        return details;
    }''', TASK_ID)

    print(f"Fetched {len(audits)} audit details.")
    for i, a in enumerate(audits):
        print(f"\n================ AUDIT #{i+1} ================")
        print(f"ID: {a.get('id') or a.get('qc_audit_id')}")
        print(f"Created: {a.get('created_at')} by {a.get('created_by')}")
        print(f"Status: {a.get('status')} | Verdict: {a.get('verdict')} | Global Pass: {a.get('global_pass')}")
        print(f"Pass count: {a.get('pass_count')}, Fail count: {a.get('fail_count')}")
        findings = a.get('findings') or []
        print(f"Findings ({len(findings)}):")
        for f in findings:
            print(f"  * [{f.get('severity')}] {f.get('title')}: {f.get('description')}")
        
        # Check failing tests
        test_results = a.get('test_results') or []
        failing_tests = [t for t in test_results if t.get('status') != 'passed']
        if failing_tests:
            print(f"Failing tests ({len(failing_tests)}):")
            for ft in failing_tests:
                print(f"  - {ft.get('name')}: status={ft.get('status')}")
                if ft.get('failure_message'):
                    print(f"    Message: {ft.get('failure_message')}")
                if ft.get('findings'):
                    for f in ft.get('findings'):
                        print(f"    Finding: [{f.get('severity')}] {f.get('title')}: {f.get('description')}")
        else:
            print(f"All {len(test_results)} test_results passed!")

    await p.stop()

if __name__ == '__main__':
    asyncio.run(check_audits_deep())
