import asyncio
import sys
import json
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def inspect_rf():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    details = await page.evaluate('''() => {
        const header = Array.from(document.querySelectorAll('*')).find(e => e.innerText === 'REVIEWER FEEDBACK');
        if (!header) return { error: "Header not found" };

        let container = header.parentElement;
        while (container && !container.className.includes('border') && container.tagName !== 'BODY') {
            container = container.parentElement;
        }

        const inputs = Array.from(container.querySelectorAll('textarea, input, p, div, span, label')).map(el => ({
            tag: el.tagName,
            text: el.innerText ? el.innerText.trim() : null,
            value: el.value ? el.value.trim() : null,
            placeholder: el.placeholder || null
        })).filter(x => x.text || x.value);

        return {
            fullText: container.innerText,
            inputs: inputs.slice(0, 30)
        };
    }''')

    print("=== REVIEWER FEEDBACK BOX DETAILS ===")
    print(details.get('fullText'))
    print("=====================================")

    # Let's also check if there are any reviewer notes or transition notes in the API
    api_notes = await page.evaluate('''async (taskId) => {
        const token = await window.Clerk.session.getToken({ skipCache: true });
        const headers = {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json',
            'x-campaign-id': localStorage.getItem('x-campaign-id') || 'camp_75099d23386f4394ab7596a5ea538da8',
            'x-company-id': localStorage.getItem('x-company-id') || 'comp_2fa4115109d741cd94a3c409ed89e61f',
            'x-account-id': localStorage.getItem('x-account-id') || 'acct_85b680d4c5ba49a29f19c173672aebea'
        };

        const taskR = await fetch(`https://api.studio.mercor.com/tasks/${taskId}`, { headers });
        const task = await taskR.json();

        // Check if there are any reviews in /reviews/ or similar
        let reviews = null;
        try {
            const revR = await fetch(`https://api.studio.mercor.com/reviews/task/${taskId}`, { headers });
            if (revR.ok) reviews = await revR.json();
        } catch(e) {}

        // Check /task-transitions/
        let transitions = null;
        try {
            const trR = await fetch(`https://api.studio.mercor.com/task-transitions/?task_id=${taskId}`, { headers });
            if (trR.ok) transitions = await trR.json();
        } catch(e) {}

        return {
            task_status: task.status,
            assigned_to: task.assigned_to,
            custom_fields: task.custom_fields,
            reviews,
            transitions
        };
    }''', TASK_ID)

    print("\n=== API REVIEWS & TRANSITIONS ===")
    print("Task Status:", api_notes.get('task_status'))
    if api_notes.get('reviews'):
        print("Reviews:", json.dumps(api_notes.get('reviews'), indent=2))
    if api_notes.get('transitions'):
        print("Transitions:", json.dumps(api_notes.get('transitions'), indent=2))

    await p.stop()

if __name__ == '__main__':
    asyncio.run(inspect_rf())
