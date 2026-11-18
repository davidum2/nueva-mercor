import asyncio
import os
from playwright.async_api import async_playwright

TASK_ID = "task_a6c044440a2b440a9d578ad5c375ad94"
DEST_DIR = os.path.join(r"c:\desarrollo\nueva-mercor", TASK_ID, "model_a")

async def expand_all_model_a():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = browser.contexts[0].pages[0]

    # Select Model A
    await page.evaluate("""() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const m = btns.find(b => (b.innerText || '').trim() === 'Model A');
        if (m) m.click();
    }""")
    await asyncio.sleep(1.0)

    # Click LOGS
    await page.evaluate("""() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const logs = btns.find(b => (b.innerText || '').trim() === 'LOGS');
        if (logs) logs.click();
    }""")
    await asyncio.sleep(1.0)

    # Click Expand all if present
    await page.evaluate("""() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const exp = btns.find(b => (b.innerText || '').trim() === 'Expand all');
        if (exp) exp.click();
    }""")
    await asyncio.sleep(2.0)

    # Now click all 'more lines', 'show more', etc.
    total_clicked = 0
    for round_idx in range(8):
        clicked = await page.evaluate("""() => {
            const btns = Array.from(document.querySelectorAll('button')).filter(b => {
                const t = (b.innerText || '').toLowerCase();
                return t.includes('more lines') || t.includes('show more');
            });
            btns.forEach(b => {
                try { b.click(); } catch(e) {}
            });
            return btns.length;
        }""")
        print(f"Round {round_idx}: Clicked {clicked} 'more' buttons")
        total_clicked += clicked
        if clicked == 0:
            break
        await asyncio.sleep(2.0)

    print(f"Total 'more' buttons clicked: {total_clicked}")

    # Extract full text
    full_text = await page.evaluate('document.body.innerText')
    out_file = os.path.join(DEST_DIR, "all_steps_expanded.txt")
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(full_text)
    print(f"Saved {out_file} ({len(full_text)} chars)")

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(expand_all_model_a())
