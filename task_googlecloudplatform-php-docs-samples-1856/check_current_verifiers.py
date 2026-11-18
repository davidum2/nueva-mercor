import asyncio
import json
from playwright.async_api import async_playwright

TASK_ID = "task_a6c044440a2b440a9d578ad5c375ad94"

async def check():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [pg for pg in browser.contexts[0].pages if 'rubric' in pg.url and TASK_ID in pg.url][0]
    
    result = await page.evaluate("""async ({ taskId }) => {
        const token = await window.Clerk.session.getToken({ skipCache: true });
        const campaignId = localStorage.getItem('x-campaign-id') || 'camp_75099d23386f4394ab7596a5ea538da8';
        const companyId = localStorage.getItem('x-company-id') || 'comp_2fa4115109d741cd94a3c409ed89e61f';
        const accountId = localStorage.getItem('x-account-id') || 'acct_85b680d4c5ba49a29f19c173672aebea';
        
        const headers = {
            'Authorization': 'Bearer ' + token,
            'x-campaign-id': campaignId,
            'x-company-id': companyId,
            'x-account-id': accountId
        };
        
        const r = await fetch(`https://api.studio.mercor.com/verifiers/task/${taskId}`, { headers });
        const d = await r.json();
        return {
            status: r.status,
            verifiers: d.verifiers || []
        };
    }""", { "taskId": TASK_ID })
    
    print(f"Status: {result['status']}")
    print(f"Total verifiers found: {len(result['verifiers'])}")
    for i, v in enumerate(result['verifiers']):
        crit = v.get('verifier_values', {}).get('criteria', '')[:60]
        ans_a = v.get('verifier_custom_field_values', {}).get('answer_a')
        ans_b = v.get('verifier_custom_field_values', {}).get('answer_b')
        print(f"  [{i+1}] ID={v.get('verifier_id')} | idx={v.get('verifier_index')} | A={ans_a} B={ans_b} | {crit}")
        
    await p.stop()

if __name__ == '__main__':
    asyncio.run(check())
