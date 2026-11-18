import asyncio
import json
from playwright.async_api import async_playwright

async def run():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    mercor_page = None
    for ctx in browser.contexts:
        for page in ctx.pages:
            if 'mercor.com' in page.url:
                mercor_page = page
                break
        if mercor_page:
            break

    if not mercor_page:
        print("No mercor page found")
        await browser.close()
        await p.stop()
        return

    script = """async () => {
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
        
        const endpoints = {
            task_current: 'https://api.studio.mercor.com/tasks/task_74b080f5a1554daaba2595c070f210f7',
            task_history: 'https://api.studio.mercor.com/tasks/task_74b080f5a1554daaba2595c070f210f7/history',
            task_related: 'https://api.studio.mercor.com/tasks/task_74b080f5a1554daaba2595c070f210f7/related',
            task_parent: 'https://api.studio.mercor.com/tasks/task_0057084a97584d44be95a70728659de6',
            task_parent_history: 'https://api.studio.mercor.com/tasks/task_0057084a97584d44be95a70728659de6/history'
        };
        
        const res = {};
        for (const [k, url] of Object.entries(endpoints)) {
            try {
                const r = await fetch(url, { headers });
                if (r.ok) {
                    res[k] = await r.json();
                } else {
                    const txt = await r.text();
                    res[k] = { status: r.status, statusText: r.statusText, body: txt };
                }
            } catch (err) {
                res[k] = { error: err.message };
            }
        }
        return res;
    }"""
    
    data = await mercor_page.evaluate(script)
    with open('mercor_api_fetched.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
        
    for k, v in data.items():
        if isinstance(v, dict) and 'status' in v:
            print(f"{k}: Status {v['status']} {v['statusText']} -> {v.get('body')}")
        else:
            print(f"{k}: Success ({type(v).__name__})")

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
