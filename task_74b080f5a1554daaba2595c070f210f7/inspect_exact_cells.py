import asyncio
from playwright.async_api import async_playwright

async def run():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    ctx = browser.contexts[0]
    rubric_page = None
    for pg in ctx.pages:
        if '/rubric/' in pg.url:
            rubric_page = pg
            break

    cells = await rubric_page.evaluate(r"""() => {
        return {
            r2_ans_a: document.querySelector('[data-cell="1-4"]')?.innerText?.trim(),
            r2_reason_a: document.querySelector('[data-cell="1-5"]')?.innerText?.trim(),
            r2_ans_b: document.querySelector('[data-cell="1-6"]')?.innerText?.trim(),
            r2_reason_b: document.querySelector('[data-cell="1-7"]')?.innerText?.trim(),
            r3_reason_b: document.querySelector('[data-cell="2-7"]')?.innerText?.trim(),
            r7_reason_b: document.querySelector('[data-cell="6-7"]')?.innerText?.trim(),
            r8_ans_a: document.querySelector('[data-cell="7-4"]')?.innerText?.trim(),
            r8_reason_a: document.querySelector('[data-cell="7-5"]')?.innerText?.trim(),
            r10_ans_a: document.querySelector('[data-cell="9-4"]')?.innerText?.trim(),
            r10_reason_a: document.querySelector('[data-cell="9-5"]')?.innerText?.trim(),
            r11_reason_b: document.querySelector('[data-cell="10-7"]')?.innerText?.trim()
        };
    }""")
    for k, v in cells.items():
        print(f"{k}: {v}")

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
