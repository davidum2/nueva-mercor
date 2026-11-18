import asyncio
import json
from playwright.async_api import async_playwright

TASK_ID = "task_a6c044440a2b440a9d578ad5c375ad94"

async def inspect():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [pg for pg in browser.contexts[0].pages if 'mercor.com' in pg.url and 'sign-in' not in pg.url][0]

    endpoints = [
        f"https://api.studio.mercor.com/tasks/{TASK_ID}/verifiers",
        f"https://api.studio.mercor.com/tasks/{TASK_ID}/rubrics",
        f"https://api.studio.mercor.com/tasks/{TASK_ID}/rubric",
        f"https://api.studio.mercor.com/tasks/{TASK_ID}/task_verifiers"
    ]

    res = await page.evaluate("""async (urls) => {
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
        const results = {};
        for (const url of urls) {
            try {
                const r = await fetch(url, { headers });
                results[url] = { status: r.status, ok: r.ok, data: r.ok ? await r.json() : await r.text() };
            } catch(e) {
                results[url] = { error: e.message };
            }
        }
        return results;
    }""", endpoints)

    print("API Endpoint Checks:")
    for url, r in res.items():
        print(f"\nURL: {url}")
        print(f"Status: {r.get('status')}, OK: {r.get('ok')}")
        if r.get('ok'):
            d = r.get('data')
            print(f"Data type: {type(d)}, len: {len(d) if isinstance(d, (list, dict)) else 'N/A'}")
            print("Preview:", json.dumps(d, indent=2)[:300])
        else:
            print("Response:", r.get('data'))

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(inspect())
