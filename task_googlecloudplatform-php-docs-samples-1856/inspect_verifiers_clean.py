import asyncio
import json
from playwright.async_api import async_playwright

async def get():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [pg for pg in browser.contexts[0].pages if 'mercor.com' in pg.url and 'sign-in' not in pg.url][0]

    data = await page.evaluate('''async () => {
        const token = await window.Clerk.session.getToken();
        const campaignId = localStorage.getItem('x-campaign-id') || 'camp_75099d23386f4394ab7596a5ea538da8';
        const companyId = localStorage.getItem('x-company-id') || '';
        const accountId = localStorage.getItem('x-account-id') || '';
        const headers = {
            'Authorization': 'Bearer ' + token,
            'x-campaign-id': campaignId,
            'x-company-id': companyId,
            'x-account-id': accountId
        };
        const r74b = await fetch('https://api.studio.mercor.com/verifiers/task/task_74b080f5a1554daaba2595c070f210f7', { headers });
        const ra6c = await fetch('https://api.studio.mercor.com/verifiers/task/task_a6c044440a2b440a9d578ad5c375ad94', { headers });
        return {
            v74b: await r74b.json(),
            va6c: await ra6c.json()
        };
    }''')

    v74b = data['v74b']
    va6c = data['va6c']

    print(f"Task 74b Verifiers count: {len(v74b) if isinstance(v74b, list) else v74b}")
    print(f"Task a6c Verifiers count: {len(va6c) if isinstance(va6c, list) else va6c}")

    if isinstance(v74b, list) and len(v74b) > 0:
        print("\n=== SAMPLE VERIFIER FROM 74B ===")
        print(json.dumps(v74b[0], indent=2))
        with open('sample_verifiers_74b.json', 'w', encoding='utf-8') as f:
            json.dump(v74b, f, indent=2, ensure_ascii=False)

    if isinstance(va6c, list):
        print(f"\nTask a6c has {len(va6c)} verifiers.")
        with open('sample_verifiers_a6c.json', 'w', encoding='utf-8') as f:
            json.dump(va6c, f, indent=2, ensure_ascii=False)

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(get())
