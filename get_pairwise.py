import asyncio
import json
from playwright.async_api import async_playwright

TASK_ID = 'task_08ccf272669347c3af63de71b2ecb5e5'

async def get_pairwise_options():
    p = await async_playwright().start()
    b = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [pg for pg in b.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url][0]

    opts = await page.evaluate('''async () => {
        const labels = Array.from(document.querySelectorAll('label'));
        const pLabel = labels.find(l => l.innerText.includes('Pairwise Evaluation'));
        if (!pLabel) return [];
        const btn = pLabel.parentElement.querySelector('button[role="combobox"]');
        if (!btn) return [];
        btn.click();
        await new Promise(r => setTimeout(r, 600));
        const items = Array.from(document.querySelectorAll('[role="option"]'));
        const res = items.map(it => it.innerText.trim());
        // close menu by clicking outside or pressing Escape
        document.body.click();
        return res;
    }''')
    print('Pairwise options:', opts)
    await b.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(get_pairwise_options())
