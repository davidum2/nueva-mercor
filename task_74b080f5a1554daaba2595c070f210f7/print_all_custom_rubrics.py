import asyncio
import json
from playwright.async_api import async_playwright

async def print_all():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = browser.contexts[0].pages[0]

    data = await page.evaluate("""async () => {
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
        const r = await fetch('https://api.studio.mercor.com/tasks/task_74b080f5a1554daaba2595c070f210f7', { headers });
        return await r.json();
    }""")

    cf = data.get('custom_fields', {})
    for i in range(1, 16):
        num = f"{i:02d}"
        print(f"=== RUBRIC {i} ===")
        print(f"  Ans A: {cf.get(f'field_ta_rubric_{num}_answer_a')}")
        print(f"  Rea A: {cf.get(f'field_ta_rubric_{num}_reason_a')}")
        print(f"  Ans B: {cf.get(f'field_ta_rubric_{num}_answer_b')}")
        print(f"  Rea B: {cf.get(f'field_ta_rubric_{num}_reason_b')}")
        print()

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(print_all())
