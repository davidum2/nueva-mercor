import asyncio
from playwright.async_api import async_playwright

async def inspect():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page0 = browser.contexts[0].pages[0]
    data0 = await page0.evaluate("""() => {
        const cbs = Array.from(document.querySelectorAll('[role="combobox"]')).map((el, i) => {
            const parent = el.closest('div')?.parentElement?.parentElement?.innerText || '';
            const label = parent.split('\\n')[0];
            return { i, text: el.innerText.trim(), label: label.slice(0, 50) };
        });
        return cbs;
    }""")
    print("Page 0 comboboxes:")
    for c in data0:
        print(c)

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(inspect())
