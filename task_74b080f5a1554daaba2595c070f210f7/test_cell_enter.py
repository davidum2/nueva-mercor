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

    # Click on data-cell="1-1"
    cell = mercor_page.locator('[data-cell="1-1"]')
    await cell.click()
    await asyncio.sleep(0.5)
    await mercor_page.keyboard.press('Enter')
    await asyncio.sleep(0.5)

    res = await mercor_page.evaluate("""() => {
        const cell = document.querySelector('[data-cell="1-1"]');
        const input = cell ? cell.querySelector('input, textarea') : null;
        const globalActive = document.activeElement ? {
            tag: document.activeElement.tagName,
            type: document.activeElement.type,
            className: document.activeElement.className,
            value: document.activeElement.value
        } : null;
        return {
            hasInputInCell: !!input,
            inputHTML: input ? input.outerHTML : null,
            globalActive
        };
    }""")
    print("Edit mode check:", res)

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
