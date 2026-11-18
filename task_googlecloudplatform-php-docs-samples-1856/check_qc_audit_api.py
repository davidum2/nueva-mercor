import asyncio
import sys
import json
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def check_api():
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

        const res = await fetch(`https://api.studio.mercor.com/qc-audits/?subject_kind=task&subject_id=${taskId}&qc_spec_id=qcspec_6f94d16495ca0467e1ec371b`, { headers });
        return await res.json();
    }''', TASK_ID)

    print("Audits response:", json.dumps(data, indent=2))

    # Also let's check the Navigation screen
    nav_item = page.locator('span:text-is("Navigation")')
    if await nav_item.count() > 0:
        await nav_item.first.click()
        await asyncio.sleep(2)
        await page.evaluate('''() => {
            const el = Array.from(document.querySelectorAll('*')).find(e => e.innerText && e.innerText.startsWith('Before you submit'));
            if (el) el.scrollIntoView({ behavior: 'instant', block: 'start' });
        }''')
        await asyncio.sleep(1)
        await page.screenshot(path='current_checklist_after_rerun.png')
        print("Saved current_checklist_after_rerun.png")

    await p.stop()

if __name__ == '__main__':
    asyncio.run(check_api())
