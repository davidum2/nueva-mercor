import asyncio
import json
from playwright.async_api import async_playwright

async def get_live_task():
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
    print("Fetched live task custom_fields:")
    for i in range(1, 16):
        num = f"{i:02d}"
        ans_a = cf.get(f"field_ta_rubric_{num}_answer_a")
        reas_a = cf.get(f"field_ta_rubric_{num}_reason_a", "")
        ans_b = cf.get(f"field_ta_rubric_{num}_answer_b")
        reas_b = cf.get(f"field_ta_rubric_{num}_reason_b", "")
        print(f"R{i:02d}: A=[{ans_a}] {reas_a[:50]}... | B=[{ans_b}] {reas_b[:50]}...")

    with open('live_task_custom_fields.json', 'w', encoding='utf-8') as f:
        json.dump(cf, f, indent=2)

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(get_live_task())
