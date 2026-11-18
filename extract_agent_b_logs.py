import asyncio
import os
import re
import json
from playwright.async_api import async_playwright

TASK_DIR = os.path.join(os.getcwd(), "task_74b080f5a1554daaba2595c070f210f7", "model_b")
os.makedirs(TASK_DIR, exist_ok=True)

async def main():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [p for ctx in browser.contexts for p in ctx.pages if 'mercor.com' in p.url][0]

    # Ensure Trajectory Viewer is open
    await page.locator('li button').filter(has_text='Trajectory Viewer').first.click()
    await asyncio.sleep(1.0)

    # Ensure Model B is active
    await page.locator('button').filter(has_text='Model B').first.click()
    await asyncio.sleep(1.5)

    # Ensure LOGS is active
    await page.locator('button').filter(has_text='LOGS').first.click()
    await asyncio.sleep(1.5)

    # Click Expand all
    print("Clicking Expand all for Model B...")
    try:
        await page.locator('button').filter(has_text='Expand all').first.click(timeout=3000)
    except Exception as e:
        print("Expand all not clickable or already expanded:", e)
    await asyncio.sleep(3.0)

    # Expand any remaining 'Show more'
    print("Expanding nested 'Show more' buttons...")
    for round_idx in range(5):
        expanded = await page.evaluate('''() => {
            const btns = Array.from(document.querySelectorAll('button')).filter(b => {
                const t = b.innerText.toLowerCase();
                return t.includes('more lines') || t.includes('show more');
            });
            btns.forEach(b => {
                try { b.click(); } catch(e) {}
            });
            return btns.length;
        }''')
        print(f"Round {round_idx}: Clicked {expanded} 'Show more' buttons")
        if expanded == 0:
            break
        await asyncio.sleep(1.5)

    # Extract full text
    full_text = await page.evaluate('document.body.innerText')
    raw_file = os.path.join(TASK_DIR, "all_steps_expanded_b.txt")
    with open(raw_file, "w", encoding="utf-8") as f:
        f.write(full_text)
    print(f"Saved all_steps_expanded_b.txt ({len(full_text)} chars)")

if __name__ == "__main__":
    asyncio.run(main())
