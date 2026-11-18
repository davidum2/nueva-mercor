import asyncio
import sys
import json
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def inspect():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    # Find the buttons inside the AutoQC finding card
    buttons = await page.evaluate('''() => {
        const btns = Array.from(document.querySelectorAll('button')).filter(b => {
            const t = b.innerText || '';
            return t === 'Agree' || t === 'Dispute' || t === 'Add to rerun' || t.includes('Rerun') || t === 'Show more';
        }).map(b => ({
            text: b.innerText,
            disabled: b.disabled,
            className: b.className
        }));
        return btns;
    }''')

    print("Found buttons in AutoQC card:", json.dumps(buttons, indent=2))

    # Also check what qc-audits API returns
    audit_data = await page.evaluate('''async (taskId) => {
        const token = await window.Clerk.session.getToken({ skipCache: true });
        const headers = {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json',
            'x-campaign-id': localStorage.getItem('x-campaign-id') || 'camp_75099d23386f4394ab7596a5ea538da8',
            'x-company-id': localStorage.getItem('x-company-id') || 'comp_2fa4115109d741cd94a3c409ed89e61f',
            'x-account-id': localStorage.getItem('x-account-id') || 'acct_85b680d4c5ba49a29f19c173672aebea'
        };

        const res = await fetch(`https://api.studio.mercor.com/qc-audits/?subject_kind=task&subject_id=${taskId}&qc_spec_id=qcspec_6f94d16495ca0467e1ec371b`, { headers });
        return await res.json();
    }''', TASK_ID)

    print("=== QC AUDITS API RESPONSE ===")
    if isinstance(audit_data, list):
        print(f"Total audit runs: {len(audit_data)}")
        if len(audit_data) > 0:
            latest = audit_data[-1]
            print("Latest audit keys:", list(latest.keys()))
            print("Latest audit status:", latest.get('status'))
            print("Latest audit test_results count:", len(latest.get('test_results', [])))
            for tr in latest.get('test_results', []):
                t_name = tr.get('name') or tr.get('test_name') or tr.get('qc_test_name')
                t_status = tr.get('status') or tr.get('result')
                print(f"  Test: {t_name} -> {t_status}")
    elif isinstance(audit_data, dict):
        print("Audit dict keys:", list(audit_data.keys()))
        results = audit_data.get('qc_audits', [])
        print(f"Total qc_audits: {len(results)}")
        if len(results) > 0:
            latest = results[-1]
            print("Latest audit id:", latest.get('id') or latest.get('qc_audit_id'))
            print("Latest test results:", latest.get('test_results'))

    await p.stop()

if __name__ == '__main__':
    asyncio.run(inspect())
