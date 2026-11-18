import asyncio
import json
from playwright.async_api import async_playwright

async def inspect():
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
        const r = await fetch('https://api.studio.mercor.com/verifiers/eval-definitions', { headers });
        return await r.json();
    }''')

    with open('eval_definitions.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    if isinstance(data, list):
        for item in data:
            print('eval_config_id:', item.get('eval_config_id'), '| name:', item.get('name'))
            for fld in item.get('custom_fields', []):
                print(f"  Field: {fld.get('name')} | Type: {fld.get('type')}")
                if fld.get('options'):
                    print(f"    Options: {[o.get('value') or o.get('label') for o in fld.get('options')]}")
    else:
        print("Response:", data)

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(inspect())
