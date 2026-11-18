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

    # Click on data-cell="14-3"
    cell = mercor_page.locator('[data-cell="14-3"]')
    await cell.click()
    await asyncio.sleep(0.5)
    await mercor_page.keyboard.press('Enter')
    await asyncio.sleep(0.5)

    res = await mercor_page.evaluate("""() => {
        const cell = document.querySelector('[data-cell="14-3"]');
        const popover = document.querySelector('[data-radix-popper-content-wrapper], [role="dialog"], [role="listbox"], [role="menu"]');
        return {
            cellHTML: cell.innerHTML,
            hasPopover: !!popover,
            popoverHTML: popover ? popover.innerHTML : null
        };
    }""")
    print("Source cell click check:", res)

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
