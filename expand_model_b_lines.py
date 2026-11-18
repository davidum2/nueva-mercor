import asyncio
import os
from playwright.async_api import async_playwright

TASK_DIR = os.path.join(os.getcwd(), "task_74b080f5a1554daaba2595c070f210f7", "model_b")

async def main():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [p for ctx in browser.contexts for p in ctx.pages if 'mercor.com' in p.url][0]

    # Ensure Trajectory Viewer is open
    await page.locator('li button').filter(has_text='Trajectory Viewer').first.click()
    await asyncio.sleep(1.0)

    # Ensure Model B is active
    await page.locator('button').filter(has_text='Model B').first.click()
    await asyncio.sleep(1.0)

    # Ensure LOGS is active
    await page.locator('button').filter(has_text='LOGS').first.click()
    await asyncio.sleep(1.0)

    # Click all buttons containing "Show" and "lines"
    clicked_total = 0
    for round_idx in range(5):
        clicked = await page.evaluate('''() => {
            const btns = Array.from(document.querySelectorAll('button')).filter(b => {
                const t = b.innerText.toLowerCase();
                return (t.includes('show') && t.includes('lines')) || t.includes('show more');
            });
            btns.forEach(b => {
                try { b.click(); } catch(e) {}
            });
            return btns.length;
        }''')
        clicked_total += clicked
        print(f"Round {round_idx}: Clicked {clicked} expand buttons")
        if clicked == 0:
            break
        await asyncio.sleep(1.5)

    full_text = await page.evaluate('document.body.innerText')
    out_path = os.path.join(TASK_DIR, "page_model_b_fully_expanded.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(full_text)
    print(f"Saved page_model_b_fully_expanded.txt ({len(full_text)} chars)")

if __name__ == "__main__":
    asyncio.run(main())
