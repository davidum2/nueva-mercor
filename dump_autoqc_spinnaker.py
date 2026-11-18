import asyncio
from playwright.async_api import async_playwright

TASK_ID = 'task_08ccf272669347c3af63de71b2ecb5e5'

async def inspect_autoqc_results():
    p = await async_playwright().start()
    b = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [pg for pg in b.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url][0]

    # Expand Deliverable AutoQC if needed
    await page.evaluate('''() => {
        const header = Array.from(document.querySelectorAll('div')).find(d => {
            return (d.innerText || '').trim() === 'DELIVERABLE AUTOQC' && d.className.includes('cursor-pointer');
        });
        if (header && header.parentElement && header.parentElement.getBoundingClientRect().height < 50) {
            header.click();
        }
    }''')
    await asyncio.sleep(1.5)

    res = await page.evaluate('''() => {
        const header = Array.from(document.querySelectorAll('div')).find(d => {
            return (d.innerText || '').trim() === 'DELIVERABLE AUTOQC' && d.className.includes('cursor-pointer');
        });
        if (header && header.parentElement) {
            return header.parentElement.innerText;
        }
        return 'not found';
    }''')
    print("=== DELIVERABLE AUTOQC FULL CONTENT ===")
    print(res)

    await b.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(inspect_autoqc_results())
