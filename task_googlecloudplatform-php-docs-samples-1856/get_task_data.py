import asyncio
import json
from playwright.async_api import async_playwright

TASK_ID = "task_a6c044440a2b440a9d578ad5c375ad94"

async def get_live_task():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    
    # Find active logged-in page
    page = None
    for pg in browser.contexts[0].pages:
        if 'mercor.com' in pg.url and 'sign-in' not in pg.url:
            page = pg
            break

    if not page:
        print("No logged-in Mercor page found!")
        await browser.close()
        await p.stop()
        return

    print("Using page:", page.url)

    data = await page.evaluate("""async (taskId) => {
        const token = await window.Clerk.session.getToken();
        const campaignId = localStorage.getItem('x-campaign-id') || 'camp_75099d23386f4394ab7596a5ea538da8';
        const companyId = localStorage.getItem('x-company-id') || '';
        const accountId = localStorage.getItem('x-account-id') || '';
        const headers = {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json',
            'x-campaign-id': campaignId,
            'x-company-id': companyId,
            'x-account-id': accountId
        };
        const r = await fetch(`https://api.studio.mercor.com/tasks/${taskId}`, { headers });
        return await r.json();
    }""", TASK_ID)

    print("Task Keys:", list(data.keys()))
    cf = data.get('custom_fields', {})
    print(f"custom_fields count: {len(cf)}")

    print("field_rubric_count:", cf.get('field_rubric_count'))
    for k in sorted(cf.keys()):
        if 'rubric' in k:
            print(f"  {k}: {repr(cf[k])[:80]}")

    with open('current_live_task.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("Saved current_live_task.json")

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(get_live_task())
