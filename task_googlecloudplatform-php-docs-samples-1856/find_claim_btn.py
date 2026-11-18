import asyncio
from playwright.async_api import async_playwright

async def find_claim():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = browser.contexts[0].pages[0]

    btns = await page.evaluate("""() => {
        return Array.from(document.querySelectorAll('button')).map(b => b.innerText.trim()).filter(Boolean);
    }""")
    print("All buttons on page:")
    for b in btns:
        if any(k in b.lower() for k in ['claim', 'start', 'save', 'task', 'review', 'annotate']):
            print(" ", b)

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(find_claim())
