import asyncio
from playwright.async_api import async_playwright

TASK_ID = 'task_08ccf272669347c3af63de71b2ecb5e5'

async def click_deliverable_autoqc():
    p = await async_playwright().start()
    b = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [pg for pg in b.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url][0]

    res = await page.evaluate('''() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const autoqcBtn = btns.find(b => b.innerText && b.innerText.trim() === 'Deliverable AutoQC');
        if (autoqcBtn) {
            autoqcBtn.scrollIntoView({ behavior: 'instant', block: 'center' });
            autoqcBtn.click();
            return { ok: true, text: autoqcBtn.innerText };
        }
        return { ok: false };
    }''')
    print('Click Deliverable AutoQC result:', res)

    await asyncio.sleep(2)

    # Now let's see what buttons exist now
    new_buttons = await page.evaluate('''() => {
        return Array.from(document.querySelectorAll('button')).map(b => b.innerText.trim()).filter(t => t.length > 0 && t.length < 60);
    }''')
    print('Buttons after clicking Deliverable AutoQC:')
    for b_text in sorted(set(new_buttons)):
        if any(k in b_text.lower() for k in ['run', 'auto', 'qc', 'rerun', 'latest', 'test']):
            print('  ->', b_text)

    # Let's also check what innerText appears under the DELIVERABLE AUTOQC container
    container_text = await page.evaluate('''() => {
        const headers = Array.from(document.querySelectorAll('*')).filter(e => (e.innerText || '').trim() === 'DELIVERABLE AUTOQC');
        if (headers.length > 0) {
            let p = headers[0].parentElement;
            while (p && p.innerText.length < 200) p = p.parentElement;
            return p ? p.innerText.substring(0, 1000) : 'no parent';
        }
        return 'no header';
    }''')
    print('\nDELIVERABLE AUTOQC container text:\n', container_text)

    await b.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(click_deliverable_autoqc())
