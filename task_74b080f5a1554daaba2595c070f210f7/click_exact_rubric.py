import asyncio
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

    # Click element #1: 'Rubric'
    clicked = await mercor_page.evaluate("""() => {
        const btns = Array.from(document.querySelectorAll('button')).filter(b => b.innerText.trim() === 'Rubric');
        if (btns.length > 0) {
            btns[0].click();
            return { clicked: true, className: btns[0].className };
        }
        return { clicked: false };
    }""")
    print("Clicked button 'Rubric':", clicked)
    await asyncio.sleep(2)

    status = await mercor_page.evaluate("""() => {
        const txt = document.body.innerText;
        const tables = document.querySelectorAll('table');
        return {
            hasTaskRubric: txt.includes('Task Rubric'),
            hasSpreadsheet: txt.includes('Spreadsheet'),
            tablesCount: tables.length,
            tableHeaders: Array.from(tables).map(t => Array.from(t.querySelectorAll('th')).map(th => th.innerText.trim()))
        };
    }""")
    print("Status after clicking 'Rubric':", status)

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
