import asyncio
import os
from playwright.async_api import async_playwright

async def main():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [p for ctx in browser.contexts for p in ctx.pages if 'mercor.com' in p.url][0]

    # Use playwright locator to click Model B tab
    await page.locator('button', has_text='Model B').first.click()
    await asyncio.sleep(2.0)

    states = await page.evaluate('''() => {
        const btns = Array.from(document.querySelectorAll('button')).filter(b => ['Model A', 'Model B'].includes(b.innerText.trim()));
        return btns.map(b => ({
            name: b.innerText.trim(),
            state: b.getAttribute('data-state')
        }));
    }''')
    print('States:', states)

    # Click Expand all in logs if available
    try:
        await page.locator('button', has_text='Expand all').click(timeout=2000)
    except Exception as e:
        print("Expand all not found or already expanded")

    await asyncio.sleep(1.0)
    text = await page.evaluate('document.body.innerText')
    with open('task_74b080f5a1554daaba2595c070f210f7/model_b/page_when_model_b_active.txt', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Guardado page_when_model_b_active.txt")

if __name__ == "__main__":
    asyncio.run(main())
