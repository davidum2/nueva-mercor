import asyncio
import os
from playwright.async_api import async_playwright

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

    # 2. Select Model A
    await page.evaluate('''() => {
        const btns = Array.from(document.querySelectorAll('button')).filter(b => b.innerText.trim() === 'Model A');
        if (btns.length > 0) btns[0].click();
    }''')
    await asyncio.sleep(1.0)

    # 3. Select LOGS
    await page.evaluate('''() => {
        const btns = Array.from(document.querySelectorAll('button')).filter(b => b.innerText.trim() === 'LOGS');
        if (btns.length > 0) btns[0].click();
    }''')
    await asyncio.sleep(1.0)

    # 4. Click Expand all
    clicked_expand = await page.evaluate('''() => {
        const btns = Array.from(document.querySelectorAll('button')).filter(b => b.innerText.trim() === 'Expand all');
        if (btns.length > 0) {
            btns[0].click();
            return true;
        }
        return false;
    }''')
    print("Clicked Expand all:", clicked_expand)
    await asyncio.sleep(3.0)

    # 5. Check if button now says Collapse all
    status = await page.evaluate('''() => {
        const b = Array.from(document.querySelectorAll('button')).find(btn => btn.innerText.includes('Collapse all') || btn.innerText.includes('Expand all'));
        return b ? b.innerText.trim() : 'None';
    }''')
    print("Button status:", status)

    # 6. Click any 'Show more' or 'Show X more lines' in batches
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

    # 7. Extract the complete text of the page
    full_text = await page.evaluate('document.body.innerText')
    out_file = 'task_74b080f5a1554daaba2595c070f210f7/model_a/all_steps_expanded.txt'
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(full_text)
    print(f"Saved {out_file} ({len(full_text)} chars)")

if __name__ == "__main__":
    asyncio.run(main())
