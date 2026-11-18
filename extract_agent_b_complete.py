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

    # 1. Nav to Trajectory Viewer
    await page.evaluate('''() => {
        const btns = Array.from(document.querySelectorAll('li button')).filter(b => b.innerText.trim() === 'Trajectory Viewer');
        if (btns.length > 0) btns[0].click();
    }''')
    await asyncio.sleep(1.5)

    # 2. Select Model B
    print("Selecting Model B...")
    await page.evaluate('''() => {
        const btns = Array.from(document.querySelectorAll('button')).filter(b => b.innerText.trim() === 'Model B');
        if (btns.length > 0) btns[0].click();
    }''')
    await asyncio.sleep(1.5)

    # 3. Select LOGS
    print("Selecting LOGS...")
    await page.evaluate('''() => {
        const btns = Array.from(document.querySelectorAll('button')).filter(b => b.innerText.trim() === 'LOGS');
        if (btns.length > 0) btns[0].click();
    }''')
    await asyncio.sleep(1.5)

    # 4. Click Expand all
    print("Clicking Expand all...")
    await page.evaluate('''() => {
        const btns = Array.from(document.querySelectorAll('button')).filter(b => b.innerText.trim() === 'Expand all');
        if (btns.length > 0) btns[0].click();
    }''')
    await asyncio.sleep(3.0)

    # 5. Expand nested 'Show more' / 'more lines'
    print("Expanding nested 'Show more' and code blocks for Model B...")
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

    # 6. Extract full text
    full_text = await page.evaluate('document.body.innerText')
    raw_file = os.path.join(TASK_DIR, "all_steps_expanded.txt")
    with open(raw_file, "w", encoding="utf-8") as f:
        f.write(full_text)
    print(f"Saved all_steps_expanded.txt ({len(full_text)} chars)")

if __name__ == "__main__":
    asyncio.run(main())
