import asyncio
import json
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def find_feedback():
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

        const histRes = await fetch(`https://api.studio.mercor.com/tasks/${taskId}/history`, { headers });
        const historyData = await histRes.json();
        const history = historyData.history || historyData;

        // Find the last two entries: 
        // one when Edgar submitted (17:33) or Tyler claimed (17:51), and one when Tyler rejected (17:53)
        const lastEntry = history[history.length - 1];
        const prevEntry = history[history.length - 2];

        // Diff all keys of lastEntry vs prevEntry
        const diff = {};
        for (const k of Object.keys(lastEntry)) {
            if (JSON.stringify(lastEntry[k]) !== JSON.stringify(prevEntry[k])) {
                diff[k] = {
                    prev: prevEntry[k],
                    last: lastEntry[k]
                };
            }
        }

        // Also check custom_fields diff specifically
        const cfDiff = {};
        const lastCf = lastEntry.custom_fields || {};
        const prevCf = prevEntry.custom_fields || {};
        const allCfKeys = new Set([...Object.keys(lastCf), ...Object.keys(prevCf)]);
        for (const k of allCfKeys) {
            if (JSON.stringify(lastCf[k]) !== JSON.stringify(prevCf[k])) {
                cfDiff[k] = {
                    prev: prevCf[k],
                    last: lastCf[k]
                };
            }
        }

        // Check if there are task comments or thread messages
        let comments = null;
        try {
            const commRes = await fetch(`https://api.studio.mercor.com/tasks/${taskId}/comments`, { headers });
            comments = await commRes.json();
        } catch(e) {
            comments = e.message;
        }

        // Check if there's any feedback in the task object itself
        const taskRes = await fetch(`https://api.studio.mercor.com/tasks/${taskId}`, { headers });
        const task = await taskRes.json();

        return {
            diffKeys: Object.keys(diff),
            diffDetails: diff,
            cfDiff: cfDiff,
            comments: comments,
            taskReviewerFeedback: task.reviewer_feedback || task.feedback || task.rejection_reason || task.review_notes,
            taskNotes: task.notes
        };
    }''', TASK_ID)

    print("=== DIFF BETWEEN PREV AND LAST ENTRY ===")
    print("Diff keys:", res['diffKeys'])
    for k in res['diffKeys']:
        if k != 'custom_fields':
            print(f"\n[{k}]:")
            print("Prev:", json.dumps(res['diffDetails'][k]['prev'], indent=2)[:300])
            print("Last:", json.dumps(res['diffDetails'][k]['last'], indent=2)[:300])

    print("\n=== CUSTOM FIELDS DIFF ===")
    for k, v in res['cfDiff'].items():
        print(f"\n[{k}]:")
        print("  Prev:", str(v['prev'])[:200])
        print("  Last:", str(v['last'])[:200])

    print("\n=== COMMENTS / THREADS ===")
    print(json.dumps(res['comments'], indent=2))

    print("\n=== TASK FIELDS ===")
    print("taskReviewerFeedback:", res['taskReviewerFeedback'])
    print("taskNotes:", res['taskNotes'])

    await p.stop()

if __name__ == '__main__':
    asyncio.run(find_feedback())
