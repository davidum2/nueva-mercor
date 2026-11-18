import asyncio
from playwright.async_api import async_playwright

async def find_string():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page0 = browser.contexts[0].pages[0]

    # Search for "input-side" or "missing input-side" in page HTML or evaluate
    res = await page0.evaluate("""() => {
        const html = document.documentElement.innerHTML;
        const idx = html.indexOf('input-side');
        const idx2 = html.indexOf('symlink as an input');
        const idx3 = html.indexOf('when the symlink shows up as a spawn input');
        return {
            has_input_side: idx !== -1,
            snippet1: idx !== -1 ? html.slice(Math.max(0, idx - 100), idx + 100) : null,
            has_spawn_input: idx3 !== -1,
            snippet3: idx3 !== -1 ? html.slice(Math.max(0, idx3 - 100), idx3 + 100) : null,
        };
    }""")
    print("Search results:", res)

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(find_string())
