import asyncio
import json
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def get_tyler_feedback():
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

        // 1. Task history entries (all of them)
        const histRes = await fetch(`https://api.studio.mercor.com/tasks/${taskId}/history`, { headers });
        const history = await histRes.json();

        // 2. Fetch the latest 5 audits with full details
        const auditsRes = await fetch(`https://api.studio.mercor.com/qc-audits/?subject_kind=task&subject_id=${taskId}&limit=20`, { headers });
        const auditsData = await auditsRes.json();
        const auditsList = auditsData.audits || (Array.isArray(auditsData) ? auditsData : []);

        // Fetch each audit individually to get full findings
        const fullAudits = await Promise.all(auditsList.slice(0, 5).map(async (a) => {
            const auditId = a.id || a.qc_audit_id;
            const r = await fetch(`https://api.studio.mercor.com/qc-audits/${auditId}`, { headers });
            return await r.json();
        }));

        // 3. Current task custom fields
        const taskRes = await fetch(`https://api.studio.mercor.com/tasks/${taskId}`, { headers });
        const taskData = await taskRes.json();

        return {
            history: history,
            fullAudits: fullAudits,
            custom_fields: taskData.custom_fields,
            task: taskData
        };
    }''', TASK_ID)

    print("=== TASK HISTORY (LAST 3 ENTRIES) ===")
    hist_data = data.get('history') or []
    if isinstance(hist_data, dict):
        hist = hist_data.get('history') or hist_data.get('tasks') or hist_data.get('items') or [hist_data]
    else:
        hist = hist_data
    for h in hist[-5:]:
        print(f"\n--- Entry at {h.get('updated_at')} by {h.get('updated_by_user_name')} ---")
        print(f"Status: {h.get('task_status_defn', {}).get('status_name')}")
        print(f"Transition edge: {h.get('task_latest_edge', {}).get('transition_name')} (ID: {h.get('task_latest_edge', {}).get('edge_id')})")
        print(f"Notes / Reason: {h.get('notes')}")
        # Look for any feedback field
        cf = h.get('custom_fields') or {}
        if cf.get('field_adj_rationale'):
            print(f"History field_adj_rationale: {cf.get('field_adj_rationale')[:300]}...")

    print("\n=== TYLER M AUDITS AND FINDINGS ===")
    for a in data.get('fullAudits', []):
        print(f"\nAudit ID: {a.get('id') or a.get('qc_audit_id')} | Created: {a.get('created_at')} | Status: {a.get('status')}")
        findings = a.get('findings') or []
        print(f"Total findings: {len(findings)}")
        for f in findings:
            print(f"  [{f.get('severity')}] {f.get('title')}")
            print(f"    Description: {f.get('description')}")
            if f.get('suggested_fix'):
                print(f"    Suggested Fix: {f.get('suggested_fix')}")

    print("\n=== CURRENT CUSTOM FIELDS RATIONALE ===")
    cf = data.get('custom_fields') or {}
    print("field_adj_rationale:")
    print(cf.get('field_adj_rationale'))
    print("\nfield_1e32bd048d564685ba8ec51f9af11c70 (Comparative Rationale):")
    print(cf.get('field_1e32bd048d564685ba8ec51f9af11c70'))

    await p.stop()

if __name__ == '__main__':
    asyncio.run(get_tyler_feedback())
