import asyncio
import json
from playwright.async_api import async_playwright

TASK_ID = 'task_08ccf272669347c3af63de71b2ecb5e5'

async def check_ui_fields():
    p = await async_playwright().start()
    b = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [pg for pg in b.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url][0]

    info = await page.evaluate('''() => {
        const labels = Array.from(document.querySelectorAll('label'));
        const out = {};
        for (const l of labels) {
            const txt = l.innerText.trim();
            if (txt.includes('Task type') || txt.includes('Rubric count') || txt.includes('Pairwise Evaluation') || txt.includes('Final quality')) {
                const btn = l.parentElement.querySelector('button[role="combobox"], [role="combobox"]');
                out[txt] = btn ? btn.innerText.trim() : 'NO_BTN';
            }
        }
        return out;
    }''')
    print('UI dropdown states:', json.dumps(info, indent=2))
    await b.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(check_ui_fields())
