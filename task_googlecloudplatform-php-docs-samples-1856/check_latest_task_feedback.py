import asyncio
import json
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def check_feedback():
    p = await async_playwright().start()
    try:
        browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    except Exception as e:
        print(f"CDP connection failed: {e}", flush=True)
        await p.stop()
        return

    pages = browser.contexts[0].pages
    task_pages = [pg for pg in pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    
    if not task_pages:
        print("Task page not open in browser, opening or looking at available pages...", flush=True)
        for pg in pages:
            print("Page:", pg.url)
        page = pages[0]
        await page.goto(f"https://studio.mercor.com/annotator/tasks/{TASK_ID}/?campaignId=camp_75099d23386f4394ab7596a5ea538da8")
        await asyncio.sleep(5)
    else:
        page = task_pages[0]

    # 1. Fetch task API data, history, transitions, audits
    data = await page.evaluate('''async (taskId) => {
        const token = await window.Clerk.session.getToken({ skipCache: true });
        const headers = {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json',
            'x-campaign-id': localStorage.getItem('x-campaign-id') || 'camp_75099d23386f4394ab7596a5ea538da8',
            'x-company-id': localStorage.getItem('x-company-id') || 'comp_2fa4115109d741cd94a3c409ed89e61f',
            'x-account-id': localStorage.getItem('x-account-id') || 'acct_85b680d4c5ba49a29f19c173672aebea'
        };

        const [taskRes, histRes, transRes, auditsRes] = await Promise.all([
            fetch(`https://api.studio.mercor.com/tasks/${taskId}`, { headers }).then(r => r.json()).catch(e => ({ error: e.message })),
            fetch(`https://api.studio.mercor.com/tasks/${taskId}/history`, { headers }).then(r => r.json()).catch(e => ({ error: e.message })),
            fetch(`https://api.studio.mercor.com/tasks/${taskId}/transitions`, { headers }).then(r => r.json()).catch(e => ({ error: e.message })),
            fetch(`https://api.studio.mercor.com/qc-audits/?subject_kind=task&subject_id=${taskId}&limit=10`, { headers }).then(r => r.json()).catch(e => ({ error: e.message }))
        ]);

        return {
            status: taskRes.status,
            custom_fields: taskRes.custom_fields,
            history: histRes,
            transitions: transRes,
            audits: auditsRes
        };
    }''', TASK_ID)

    print("=== TASK STATUS ===")
    print("Status:", data.get('status'))
    
    print("\n=== HISTORY (Recent 5) ===")
    hist = data.get('history')
    if isinstance(hist, list):
        for h in hist[-5:]:
            print(json.dumps(h, indent=2))
    elif isinstance(hist, dict):
        print(json.dumps(hist, indent=2))

    print("\n=== TRANSITIONS (Recent 5) ===")
    trans = data.get('transitions')
    if isinstance(trans, list):
        for t in trans[-5:]:
            print(json.dumps(t, indent=2))
    elif isinstance(trans, dict):
        print(json.dumps(trans, indent=2))

    print("\n=== RECENT AUDITS ===")
    audits = data.get('audits')
    if isinstance(audits, dict) and 'audits' in audits:
        audits_list = audits['audits']
    elif isinstance(audits, list):
        audits_list = audits
    else:
        audits_list = []
    
    for a in audits_list[:3]:
        print(f"Audit {a.get('id')} - Created: {a.get('created_at')} by {a.get('created_by')} - Status: {a.get('status')} - Verdict: {a.get('verdict')}")
        if a.get('findings'):
            for f in a.get('findings'):
                print(f"  Finding: {f.get('title')} ({f.get('severity')}): {f.get('description')}")

    # Check Reviewer Feedback tab in UI
    rf_tab = page.locator('span:text-is("Reviewer Feedback")')
    if await rf_tab.count() > 0:
        await rf_tab.first.click()
        await asyncio.sleep(2)
        await page.screenshot(path='reviewer_feedback_latest.png')
        print("\nSaved reviewer_feedback_latest.png")
        
        ui_text = await page.evaluate('''() => {
            const main = document.querySelector('main') || document.body;
            return main.innerText;
        }''')
        print("\n=== UI TEXT ON REVIEWER FEEDBACK TAB ===")
        print(ui_text[:2000])

    await p.stop()

if __name__ == '__main__':
    asyncio.run(check_feedback())
