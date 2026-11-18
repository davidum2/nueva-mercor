import asyncio
import json
from playwright.async_api import async_playwright

TASK_ID = 'task_08ccf272669347c3af63de71b2ecb5e5'

async def get_options():
    p = await async_playwright().start()
    b = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [pg for pg in b.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url][0]

    res = await page.evaluate('''() => {
        const labels = Array.from(document.querySelectorAll('label'));
        const out = {};
        for (const l of labels) {
            const txt = l.innerText.trim();
            if (txt.includes('Task type') || txt.includes('Rubric count') || txt.includes('Pairwise Evaluation')) {
                const parent = l.parentElement;
                const btn = parent.querySelector('button[role="combobox"], [role="combobox"], select');
                out[txt] = {
                    btnText: btn ? btn.innerText.trim() : null,
                    btnHTML: btn ? btn.outerHTML : null
                };
            }
        }
        return out;
    }''')
    print(json.dumps(res, indent=2))
    await b.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(get_options())
