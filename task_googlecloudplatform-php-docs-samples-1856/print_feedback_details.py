import asyncio
import sys
import json
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def print_fb():
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

        const taskRes = await fetch(`https://api.studio.mercor.com/tasks/${taskId}`, { headers });
        const task = await taskRes.json();

        // Check DOM for Reviewer Feedback textarea or text
        const rfCard = Array.from(document.querySelectorAll('*')).find(e => e.innerText && e.innerText.includes('REVIEWER FEEDBACK'));
        const rfText = rfCard ? rfCard.innerText : null;

        // Check transition history if present in task object
        return {
            rfText,
            taskReviewerFeedback: task.reviewer_feedback,
            taskAdjudicationRationale: task.adjudication_rationale,
            feedbackField: task.custom_fields ? task.custom_fields.field_reviewer_feedback : null,
            transitionHistory: task.task_transition_history || task.history || null
        };
    }''', TASK_ID)

    print("=== REVIEWER FEEDBACK IN DOM ===")
    print(res.get('rfText'))
    print("================================")
    print("taskReviewerFeedback:", res.get('taskReviewerFeedback'))
    print("taskAdjudicationRationale:", res.get('taskAdjudicationRationale'))
    print("feedbackField:", res.get('feedbackField'))

    if res.get('transitionHistory'):
        print("\n=== TRANSITION HISTORY ===")
        for th in res['transitionHistory']:
            print(f"From {th.get('from_state')} -> {th.get('to_state')} by {th.get('created_by')}")
            if th.get('notes') or th.get('feedback') or th.get('reason'):
                print("  Notes:", th.get('notes') or th.get('feedback') or th.get('reason'))

    await p.stop()

if __name__ == '__main__':
    asyncio.run(print_fb())
