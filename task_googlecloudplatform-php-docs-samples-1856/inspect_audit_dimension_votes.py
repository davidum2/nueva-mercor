import asyncio
import sys
import json
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def check():
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

        const res = await fetch(`https://api.studio.mercor.com/qc-audits/?subject_kind=task&subject_id=${taskId}&status=completed&limit=500`, { headers });
        const data = await res.json();
        const audits = data.audits || (Array.isArray(data) ? data : []);
        
        // Find latest audit
        const sorted = audits.toSorted((a,b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
        const latest = sorted[0];

        // Check outcome sections and dimensions
        const failingDims = [];
        for (const s of latest.outcome?.sections || []) {
            for (const d of s.dimensions || []) {
                if (d.status === 'fail') {
                    failingDims.push({
                        dim_id: d.dim_id,
                        dimension: d.dimension,
                        status: d.status,
                        votes: d.votes,
                        findings_count: d.findings?.length
                    });
                }
            }
        }

        return {
            total_audits: audits.length,
            latest_id: latest.id || latest.qc_audit_id,
            created_at: latest.created_at,
            failingDims
        };
    }''', TASK_ID)

    print("Audit failing dimensions inspection:")
    print(json.dumps(res, indent=2))

    await p.stop()

if __name__ == '__main__':
    asyncio.run(check())
