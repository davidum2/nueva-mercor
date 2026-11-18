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

    # Expand accordion if needed
    await mercor_page.evaluate("""() => {
        const table = document.querySelector('[data-cell="1-1"]');
        if (table) return;
        const els = Array.from(document.querySelectorAll('*')).filter(el => (el.innerText || '').trim() === 'RUBRIC' && el.children.length === 0);
        if (els.length > 0) els[0].parentElement.click();
    }""")
    await asyncio.sleep(1.0)

    # Click on cell 1-1
    cell = mercor_page.locator('[data-cell="1-1"]')
    await cell.scroll_into_view_if_needed()
    await cell.click()
    await asyncio.sleep(0.3)
    await mercor_page.keyboard.press('Enter')
    await asyncio.sleep(0.5)

    info = await mercor_page.evaluate("""() => {
        const cell = document.querySelector('[data-cell="1-1"]');
        const input = cell ? cell.querySelector('input, textarea') : null;
        const active = document.activeElement ? {
            tag: document.activeElement.tagName,
            type: document.activeElement.type,
            className: document.activeElement.className,
            value: document.activeElement.value
        } : null;
        return {
            hasInputInCell: !!input,
            inputTag: input?.tagName,
            active
        };
    }""")
    print("Cell enter info:", info)

    # Clean up edit mode
    await mercor_page.keyboard.press('Escape')

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
