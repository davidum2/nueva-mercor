import asyncio
import json
from playwright.async_api import async_playwright

async def inspect():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [pg for pg in browser.contexts[0].pages if 'mercor.com' in pg.url and 'sign-in' not in pg.url][0]

    res = await page.evaluate('''async () => {
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

        const checks = {};
        // Test OPTIONS /verifiers/
        try {
            const r = await fetch('https://api.studio.mercor.com/verifiers/', { method: 'OPTIONS', headers });
            checks['OPTIONS /verifiers/'] = { status: r.status, allow: r.headers.get('allow') };
        } catch(e) { checks['OPTIONS /verifiers/'] = e.message; }

        // Test OPTIONS /verifiers/task/task_a6c...
        try {
            const r = await fetch('https://api.studio.mercor.com/verifiers/task/task_a6c044440a2b440a9d578ad5c375ad94', { method: 'OPTIONS', headers });
            checks['OPTIONS /verifiers/task/'] = { status: r.status, allow: r.headers.get('allow') };
        } catch(e) { checks['OPTIONS /verifiers/task/'] = e.message; }

        // Test POST /verifiers/ with empty or mock body to see validation error
        try {
            const r = await fetch('https://api.studio.mercor.com/verifiers/', { method: 'POST', headers, body: JSON.stringify({}) });
            checks['POST /verifiers/'] = { status: r.status, data: await r.json() };
        } catch(e) { checks['POST /verifiers/'] = e.message; }

        return checks;
    }''')

    print(json.dumps(res, indent=2))

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(inspect())
