import asyncio
import sys
import json
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def check_latest_audit():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    latest_info = await page.evaluate('''async (taskId) => {
        const token = await window.Clerk.session.getToken({ skipCache: true });
        const headers = {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json',
            'x-campaign-id': localStorage.getItem('x-campaign-id') || 'camp_75099d23386f4394ab7596a5ea538da8',
            'x-company-id': localStorage.getItem('x-company-id') || 'comp_2fa4115109d741cd94a3c409ed89e61f',
            'x-account-id': localStorage.getItem('x-account-id') || 'acct_85b680d4c5ba49a29f19c173672aebea'
        };

        const res = await fetch(`https://api.studio.mercor.com/qc-audits/?subject_kind=task&subject_id=${taskId}&qc_spec_id=qcspec_6f94d16495ca0467e1ec371b`, { headers });
        const data = await res.json();
        const audits = data.audits || (Array.isArray(data) ? data : []);
        if (!audits.length) return { error: "No audits found" };

        const latest = audits[audits.length - 1];
        return {
            audit_id: latest.id || latest.qc_audit_id,
            status: latest.status,
            phase: latest.progress ? latest.progress.phase : null,
            verdict: latest.verdict,
            global_pass: latest.global_pass,
            status_counts: latest.status_counts,
            findings: latest.findings ? latest.findings.map(f => ({
                id: f.finding_id,
                title: f.title,
                severity: f.severity,
                desc: f.description,
                votes: f.votes
            })) : [],
            test_results: latest.test_results ? latest.test_results.map(t => ({
                name: t.name || t.test_name,
                status: t.status,
                findings_count: t.findings ? t.findings.length : 0
            })) : []
        };
    }''', TASK_ID)

    print("=== LATEST QC AUDIT DETAILS ===")
    print(json.dumps(latest_info, indent=2))
    print("================================")

    await p.stop()

if __name__ == '__main__':
    asyncio.run(check_latest_audit())
