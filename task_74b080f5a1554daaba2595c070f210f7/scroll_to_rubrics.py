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

    res = await mercor_page.evaluate("""() => {
        const all = Array.from(document.querySelectorAll('*'));
        const target = all.find(el => el.innerText && el.innerText.trim() === 'Task Rubric');
        if (target) {
            target.scrollIntoView({ behavior: 'instant', block: 'center' });
            return {
                found: true,
                rect: target.getBoundingClientRect()
            };
        }
        return { found: false };
    }""")
    print("Scroll to Task Rubric:", res)
    await asyncio.sleep(1)

    # Check if table and data-cells are visible
    cells_info = await mercor_page.evaluate("""() => {
        const cells = document.querySelectorAll('[data-cell]');
        return {
            count: cells.length,
            firstCell: cells.length > 0 ? cells[0].innerText.trim() : null
        };
    }""")
    print("Cells info after scroll:", cells_info)

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
