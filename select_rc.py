import asyncio
from playwright.async_api import async_playwright

TASK_ID = 'task_08ccf272669347c3af63de71b2ecb5e5'

async def select_rubric_count():
    p = await async_playwright().start()
    b = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [pg for pg in b.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url][0]

    # Find the Rubric count combobox and click it
    click_res = await page.evaluate('''async () => {
        const labels = Array.from(document.querySelectorAll('label'));
        const l = labels.find(x => x.innerText.includes('Rubric count'));
        if (!l) return { ok: false, error: 'label not found' };
        const btn = l.parentElement.querySelector('button[role="combobox"]');
        if (!btn) return { ok: false, error: 'btn not found' };
        btn.scrollIntoView({ behavior: 'instant', block: 'center' });
        btn.click();
        await new Promise(r => setTimeout(r, 600));

        // Find option 10
        const options = Array.from(document.querySelectorAll('[role="option"]'));
        const opt10 = options.find(o => o.innerText.trim() === '10');
        if (!opt10) return { ok: false, error: 'opt 10 not found', available: options.map(o => o.innerText.trim()) };
        opt10.click();
        return { ok: true };
    }''')
    print('Select rubric count 10 result:', click_res)

    await asyncio.sleep(2)

    # Check button text now
    new_text = await page.evaluate('''() => {
        const labels = Array.from(document.querySelectorAll('label'));
        const l = labels.find(x => x.innerText.includes('Rubric count'));
        const btn = l ? l.parentElement.querySelector('button[role="combobox"]') : null;
        return btn ? btn.innerText.trim() : null;
    }''')
    print('Rubric count combobox text now:', new_text)

    await b.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(select_rubric_count())
