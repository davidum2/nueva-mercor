import asyncio
from playwright.async_api import async_playwright

async def inspect_page1_full():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    ctx = browser.contexts[0]
    rubric_page = None
    for pg in ctx.pages:
        if '/rubric/' in pg.url:
            rubric_page = pg
            break

    data = await rubric_page.evaluate("""() => {
        return {
            r2_a_ans: document.querySelector('[data-cell="1-4"]')?.innerText?.trim(),
            r2_a_reason: document.querySelector('[data-cell="1-5"]')?.innerText?.trim(),
            r3_b_reason: document.querySelector('[data-cell="2-7"]')?.innerText?.trim(),
            r7_b_reason: document.querySelector('[data-cell="6-7"]')?.innerText?.trim(),
            r8_a_ans: document.querySelector('[data-cell="7-4"]')?.innerText?.trim(),
            r8_a_reason: document.querySelector('[data-cell="7-5"]')?.innerText?.trim(),
            r10_a_ans: document.querySelector('[data-cell="9-4"]')?.innerText?.trim(),
            r10_a_reason: document.querySelector('[data-cell="9-5"]')?.innerText?.trim(),
            r11_b_reason: document.querySelector('[data-cell="10-7"]')?.innerText?.trim(),
        };
    }""")
    for k, v in data.items():
        print(f"=== {k} ===")
        print(v)
        print()

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(inspect_page1_full())
