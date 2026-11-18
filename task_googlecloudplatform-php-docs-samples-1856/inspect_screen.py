import asyncio
from playwright.async_api import async_playwright

async def inspect_screen():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = browser.contexts[0].pages[0]

    # Dump the innerText of the main area
    main_text = await page.evaluate("""() => {
        const m = document.querySelector('main');
        return m ? m.innerText : document.body.innerText;
    }""")

    lines = [l.strip() for l in main_text.split('\n') if l.strip()]
    print(f"Total lines in main: {len(lines)}")
    print("First 40 lines:")
    for l in lines[:40]:
        print(" ", l)

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(inspect_screen())
