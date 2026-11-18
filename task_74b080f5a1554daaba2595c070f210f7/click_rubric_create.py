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

    if not mercor_page:
        print("No page found")
        await browser.close()
        await p.stop()
        return

    # Click Rubric (create)
    res = await mercor_page.evaluate("""() => {
        const els = Array.from(document.querySelectorAll('*')).filter(el => {
            return el.innerText && el.innerText.includes('Rubric (create)') && el.children.length === 0;
        });
        if (els.length > 0) {
            els[0].click();
            return { clicked: true, text: els[0].innerText };
        }
        return { clicked: false };
    }""")
    print("Click Rubric (create):", res)
    await asyncio.sleep(2)

    # Check tables now
    tables = await mercor_page.evaluate("""() => {
        const tables = Array.from(document.querySelectorAll('table'));
        return tables.map(t => {
            const headers = Array.from(t.querySelectorAll('th')).map(th => th.innerText.trim());
            return { headers, rows: t.querySelectorAll('tbody tr').length };
        });
    }""")
    print("Tables after clicking Rubric (create):", tables)

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
