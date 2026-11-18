import asyncio
from playwright.async_api import async_playwright

async def test_patch():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = browser.contexts[0].pages[0]

    res = await page.evaluate("""async () => {
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
        
        // Try PATCH with a single field update test or empty custom_fields
        try {
            const r = await fetch('https://api.studio.mercor.com/tasks/task_74b080f5a1554daaba2595c070f210f7', {
                method: 'PATCH',
                headers,
                body: JSON.stringify({
                    custom_fields: {
                        field_ta_rubric_02_answer_a: "YES"
                    }
                })
            });
            const body = await r.text();
            return { method: 'PATCH', status: r.status, ok: r.ok, body: body.slice(0, 300) };
        } catch(e) {
            return { error: e.message };
        }
    }""")
    print("PATCH test result:", res)

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(test_patch())
