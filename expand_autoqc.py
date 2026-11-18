import asyncio
from playwright.async_api import async_playwright

TASK_ID = 'task_08ccf272669347c3af63de71b2ecb5e5'

async def expand_autoqc():
    p = await async_playwright().start()
    b = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [pg for pg in b.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url][0]

    # Click the accordion header
    res = await page.evaluate('''() => {
        const header = Array.from(document.querySelectorAll('div')).find(d => {
            return (d.innerText || '').trim() === 'DELIVERABLE AUTOQC' && d.className.includes('cursor-pointer');
        });
        if (header) {
            header.click();
            return { ok: true, class: header.className };
        }
        return { ok: false };
    }''')
    print('Click accordion header result:', res)

    await asyncio.sleep(2)

    # Now let's see what is inside the accordion card
    card_info = await page.evaluate('''() => {
        const header = Array.from(document.querySelectorAll('div')).find(d => {
            return (d.innerText || '').trim() === 'DELIVERABLE AUTOQC' && d.className.includes('cursor-pointer');
        });
        if (header && header.parentElement) {
            const card = header.parentElement;
            return {
                height: card.getBoundingClientRect().height,
                text: card.innerText,
                buttons: Array.from(card.querySelectorAll('button')).map(b => b.innerText.trim())
            };
        }
        return null;
    }''')
    print('Card info after click:\n', card_info)

    await b.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(expand_autoqc())
