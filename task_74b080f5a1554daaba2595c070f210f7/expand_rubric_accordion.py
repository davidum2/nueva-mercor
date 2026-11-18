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

    # Click accordion header
    res = await mercor_page.evaluate("""() => {
        const els = Array.from(document.querySelectorAll('*')).filter(el => {
            return (el.innerText || '').trim() === 'RUBRIC' && el.children.length === 0;
        });
        if (els.length === 0) return { found: false };
        const header = els[0].parentElement;
        header.click();
        return { clicked: true, className: header.className };
    }""")
    print("Clicked accordion header:", res)
    await asyncio.sleep(2)

    # Check children of accordion container
    info = await mercor_page.evaluate("""() => {
        const els = Array.from(document.querySelectorAll('*')).filter(el => {
            return (el.innerText || '').trim() === 'RUBRIC' && el.children.length === 0;
        });
        if (els.length === 0) return null;
        const card = els[0].parentElement.parentElement;
        const tables = card.querySelectorAll('table');
        const cells = card.querySelectorAll('[data-cell]');
        return {
            cardChildrenCount: card.children.length,
            tablesCount: tables.length,
            cellsCount: cells.length,
            cardTextSnippet: card.innerText.substring(0, 300)
        };
    }""")
    print("Accordion info after click:", info)

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
