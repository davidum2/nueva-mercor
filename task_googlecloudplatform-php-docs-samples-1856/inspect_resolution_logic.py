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

    # Inspect React Fiber of the checklist or the finding card buttons
    res = await page.evaluate('''() => {
        // Find finding card buttons
        const agreeBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText === 'Agree');
        const disputeBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText === 'Dispute');

        function getFiber(el) {
            const k = Object.keys(el).find(key => key.startsWith('__reactFiber$'));
            return k ? el[k] : null;
        }

        let agreeProps = null;
        if (agreeBtn) {
            let f = getFiber(agreeBtn);
            while (f && !agreeProps) {
                if (f.memoizedProps && (f.memoizedProps.onClick || f.memoizedProps.onVote || f.memoizedProps.vote || f.memoizedProps.finding)) {
                    agreeProps = {
                        keys: Object.keys(f.memoizedProps),
                        findingId: f.memoizedProps.finding?.finding_id || f.memoizedProps.findingId
                    };
                }
                f = f.return;
            }
        }

        // Also check navigation checklist item Fiber
        const checklistItem = Array.from(document.querySelectorAll('*')).find(e => e.innerText && e.innerText.includes('AutoQC failures resolved'));
        let checkProps = null;
        if (checklistItem) {
            let f = getFiber(checklistItem);
            while (f && !checkProps) {
                if (f.memoizedProps && (f.memoizedProps.status !== undefined || f.memoizedProps.isValid !== undefined || f.memoizedProps.isComplete !== undefined)) {
                    checkProps = {
                        keys: Object.keys(f.memoizedProps),
                        props: f.memoizedProps
                    };
                }
                f = f.return;
            }
        }

        return {
            hasAgree: !!agreeBtn,
            hasDispute: !!disputeBtn,
            agreeProps,
            checkProps
        };
    }''')

    print("Resolution logic inspection:")
    print(json.dumps(res, indent=2))

    await p.stop()

if __name__ == '__main__':
    asyncio.run(inspect())
