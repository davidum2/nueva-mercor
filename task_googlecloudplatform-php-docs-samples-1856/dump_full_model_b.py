import asyncio
import os
from playwright.async_api import async_playwright

TASK_DIR = r"c:\desarrollo\nueva-mercor\task_googlecloudplatform-php-docs-samples-1856"
OUT_FILE = os.path.join(TASK_DIR, "model_b", "all_steps_expanded.txt")

async def extract_full_model_b():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [pg for ctx in browser.contexts for pg in ctx.pages if 'task_a6c04444' in pg.url and 'sign-in' not in pg.url][0]

    # Select Model B
    await page.evaluate('''() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const mb = btns.find(b => (b.innerText || '').trim() === 'Model B');
        if (mb) mb.click();
    }''')
    await asyncio.sleep(2.0)

    # Check if LOGS collapsible needs to be opened
    await page.evaluate('''() => {
        const triggers = Array.from(document.querySelectorAll('button[data-slot="collapsible-trigger"]'));
        const logsTrigger = triggers.find(b => (b.innerText || '').includes('LOGS'));
        if (logsTrigger && logsTrigger.getAttribute('data-state') === 'closed') {
            logsTrigger.click();
        }
    }''')
    await asyncio.sleep(2.0)

    # Click Expand all if present
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
        print(f"Round {r}: Clicked {clicked} more buttons for Model B")
        total_clicked += clicked
        if clicked == 0:
            break
        await asyncio.sleep(2.0)

    print(f"Total more buttons clicked for Model B: {total_clicked}")

    # Extract complete text
    full_text = await page.evaluate('document.body.innerText')
    with open(OUT_FILE, 'w', encoding='utf-8') as f:
        f.write(full_text)
    print(f"Saved {OUT_FILE} with {len(full_text)} characters.")

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(extract_full_model_b())
