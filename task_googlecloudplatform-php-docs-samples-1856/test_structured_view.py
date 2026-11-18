import asyncio
from playwright.async_api import async_playwright

async def click_structured():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    ctx = browser.contexts[0]
    rubric_page = [pg for pg in ctx.pages if 'task_a6c04444' in pg.url and '/rubric/' in pg.url][0]

    # Click Structured button
    print("Clicking Structured button...")
    btn = rubric_page.locator('button').filter(has_text="Structured")
    await btn.click()
    await asyncio.sleep(2.0)

    # Inspect what appears
    info = await rubric_page.evaluate('''() => {
        const btns = Array.from(document.querySelectorAll('button')).map(b => (b.innerText || '').trim()).filter(t => t.length > 0);
        const text = document.body.innerText;
        return { btns, textPreview: text.slice(0, 600) };
    }''')

    print("After clicking Structured:")
    print("Buttons:", info['btns'])
    print("\nText preview:\n", info['textPreview'])

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(click_structured())
