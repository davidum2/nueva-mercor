import asyncio
from playwright.async_api import async_playwright

async def take_screenshot():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = browser.contexts[0].pages[0]

    # Scroll to AutoQC section
    await page.evaluate("""() => {
        const el = Array.from(document.querySelectorAll('*')).find(e => (e.innerText || '').trim() === 'DELIVERABLE AUTOQC');
        if (el) el.scrollIntoView({ block: 'center' });
    }""")
    await asyncio.sleep(1.0)
    await page.screenshot(path='autoqc_passed_screen.png')
    print("Screenshot saved to autoqc_passed_screen.png")

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(take_screenshot())
