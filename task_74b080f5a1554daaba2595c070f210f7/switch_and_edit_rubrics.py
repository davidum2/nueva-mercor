import asyncio
import json
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

    if not mercor_page:
        print("No mercor page found")
        await browser.close()
        await p.stop()
        return

    # Click on Rubric tab
    clicked = await mercor_page.evaluate("""() => {
        const els = Array.from(document.querySelectorAll('*')).filter(el => {
            return el.innerText && el.innerText.trim() === 'Rubric' && el.children.length === 0;
        });
        for (const el of els) {
            el.click();
            return true;
        }
        return false;
    }""")
    print("Clicked Rubric tab:", clicked)
    await asyncio.sleep(2)

    # Inspect tables on page
    tables = await mercor_page.evaluate("""() => {
        const res = [];
        for (const t of document.querySelectorAll('table')) {
            const headers = Array.from(t.querySelectorAll('th')).map(th => th.innerText.trim());
            const rows = t.querySelectorAll('tbody tr').length;
            res.push({ headers, rows });
        }
        return res;
    }""")
    print("Tables found:", tables)

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
