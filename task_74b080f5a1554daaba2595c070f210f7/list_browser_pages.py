import asyncio
from playwright.async_api import async_playwright

async def run():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    print("All contexts:", len(browser.contexts))
    for i, ctx in enumerate(browser.contexts):
        for j, page in enumerate(ctx.pages):
            print(f"Context {i} Page {j}: {page.url}")

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
