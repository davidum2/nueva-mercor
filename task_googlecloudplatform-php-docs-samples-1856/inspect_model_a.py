import asyncio
from playwright.async_api import async_playwright

async def inspect_model_a():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = browser.contexts[0].pages[0]

    # Select Model A
    await page.evaluate("""() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const m = btns.find(b => (b.innerText || '').trim() === 'Model A');
        if (m) m.click();
    }""")
    await asyncio.sleep(1.0)

    # Check available buttons under Trajectory viewer
    btns = await page.evaluate("""() => {
        return Array.from(document.querySelectorAll('button')).map(b => b.innerText.trim()).filter(Boolean);
    }""")
    print("Buttons present with Model A selected:")
    for b in btns:
        if any(k in b for k in ['Model', 'LOGS', 'DIFF', 'Expand', 'Collapse', 'Step', 'final_answer']):
            print(" ", b)

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(inspect_model_a())
