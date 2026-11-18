import asyncio
import os
from playwright.async_api import async_playwright

TASK_DIR = r"c:\desarrollo\nueva-mercor\task_googlecloudplatform-php-docs-samples-1856"
OUT_FILE = os.path.join(TASK_DIR, "model_a", "all_steps_expanded.txt")

async def extract_full_model_a():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [pg for ctx in browser.contexts for pg in ctx.pages if 'task_a6c04444' in pg.url and 'sign-in' not in pg.url][0]

    # Ensure Model A is selected
    await page.evaluate('''() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const ma = btns.find(b => (b.innerText || '').trim() === 'Model A');
        if (ma) ma.click();
    }''')
    await asyncio.sleep(1.0)

    # Click Expand all if not already expanded
    await page.evaluate('''() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const exp = btns.find(b => (b.innerText || '').trim() === 'Expand all');
        if (exp) exp.click();
    }''')
    await asyncio.sleep(2.0)

    # Click all more lines / show more buttons in a loop
    total_clicked = 0
    for r in range(15):
        clicked = await page.evaluate('''() => {
            const btns = Array.from(document.querySelectorAll('button')).filter(b => {
                const t = (b.innerText || '').toLowerCase();
                return t.includes('more lines') || t.includes('show more');
            });
            btns.forEach(b => {
                try { b.click(); } catch(e) {}
            });
            return btns.length;
        }''')
        print(f"Round {r}: Clicked {clicked} more buttons")
        total_clicked += clicked
        if clicked == 0:
            break
        await asyncio.sleep(2.0)

    print(f"Total more buttons clicked: {total_clicked}")

    # Extract complete text
    full_text = await page.evaluate('document.body.innerText')
    with open(OUT_FILE, 'w', encoding='utf-8') as f:
        f.write(full_text)
    print(f"Saved {OUT_FILE} with {len(full_text)} characters.")

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(extract_full_model_a())
