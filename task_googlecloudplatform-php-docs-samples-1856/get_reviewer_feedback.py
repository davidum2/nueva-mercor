import asyncio
import sys
import json
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def get_feedback():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    # 1. Click Reviewer Feedback tab in sidebar
    rf_tab = page.locator('span:text-is("Reviewer Feedback")')
    if await rf_tab.count() > 0:
        await rf_tab.first.click()
        await asyncio.sleep(2)
        await page.screenshot(path='reviewer_feedback_tab.png')
        print("Saved reviewer_feedback_tab.png")

    # Read DOM text of the Reviewer Feedback section
    dom_feedback = await page.evaluate('''() => {
        const headers = Array.from(document.querySelectorAll('*')).filter(el => {
            const t = el.innerText || '';
            return t.includes('REVIEWER FEEDBACK') || t.includes('Feedback for writer') || t.includes('Adjudication rationale');
        });
        
        const inputs = Array.from(document.querySelectorAll('textarea, input, p, div')).filter(el => {
            const t = (el.innerText || el.value || '');
            return (t.includes('Feedback') || t.includes('Adjudication') || t.includes('Reject') || t.includes('Rohan') || t.includes('Ankit') || t.includes('Mayank')) && t.length < 2000;
        }).map(el => (el.value || el.innerText).trim());

        return {
            bodySnippet: document.body.innerText.slice(0, 3000),
            relevantItems: Array.from(new Set(inputs)).slice(0, 20)
        };
    }''')

    print("=== DOM FEEDBACK ITEMS ===")
    for item in dom_feedback['relevantItems']:
        print("ITEM:", item)
        print("-" * 40)

    # 2. Query API for task data & history transitions
    api_data = await page.evaluate('''async (taskId) => {
        const token = await window.Clerk.session.getToken({ skipCache: true });
        const headers = {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json',
            'x-campaign-id': localStorage.getItem('x-campaign-id') || 'camp_75099d23386f4394ab7596a5ea538da8',
            'x-company-id': localStorage.getItem('x-company-id') || 'comp_2fa4115109d741cd94a3c409ed89e61f',
            'x-account-id': localStorage.getItem('x-account-id') || 'acct_85b680d4c5ba49a29f19c173672aebea'
        };

        const taskRes = await fetch(`https://api.studio.mercor.com/tasks/${taskId}`, { headers });
        const task = await taskRes.json();

        // Check history endpoint if available
        let history = null;
        try {
            const histRes = await fetch(`https://api.studio.mercor.com/tasks/${taskId}/history`, { headers });
            if (histRes.ok) history = await histRes.json();
        } catch(e) {}

        // Check task events / transitions
        let transitions = null;
        try {
            const transRes = await fetch(`https://api.studio.mercor.com/tasks/${taskId}/transitions`, { headers });
            if (transRes.ok) transitions = await transRes.json();
        } catch(e) {}

        return {
            custom_fields: task.custom_fields,
            reviewer_notes: task.reviewer_notes,
            feedback: task.feedback,
            history,
            transitions
        };
    }''', TASK_ID)

    print("\n=== API FEEDBACK DATA ===")
    print("Reviewer notes in task:", api_data.get('reviewer_notes'))
    print("Feedback in task:", api_data.get('feedback'))
    print("History in task:", api_data.get('history'))
    print("Transitions in task:", api_data.get('transitions'))

    # Check custom_fields for feedback fields
    cf = api_data.get('custom_fields') or {}
    fb_fields = {k: v for k, v in cf.items() if 'feedback' in k.lower() or 'rationale' in k.lower() or 'review' in k.lower() or 'note' in k.lower()}
    print("\nFeedback-related custom fields:")
    print(json.dumps(fb_fields, indent=2))

    await p.stop()

if __name__ == '__main__':
    asyncio.run(get_feedback())
