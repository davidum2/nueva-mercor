import asyncio
import os
from playwright.async_api import async_playwright

TASK_DIR = r"c:\desarrollo\nueva-mercor\task_googlecloudplatform-php-docs-samples-1856"
OUT_FILE = os.path.join(TASK_DIR, "model_a", "all_steps_expanded.txt")

async def extract():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    
    # Find page with task_a6c044440a2b440a9d578ad5c375ad94
    target_page = None
    for ctx in browser.contexts:
        for pg in ctx.pages:
            if 'task_a6c044440a2b440a9d578ad5c375ad94' in pg.url and 'sign-in' not in pg.url:
                target_page = pg
                break
        if target_page:
            break

    if not target_page:
        print("Target task page not found!")
        await browser.close()
        await p.stop()
        return

    print("Found task page:", target_page.url)

    # 1. Click Trajectory Viewer
    await target_page.evaluate("""() => {
        const btns = Array.from(document.querySelectorAll('button, [role="tab"], li'));
        const tv = btns.find(b => (b.innerText || '').trim().includes('Trajectory Viewer'));
        if (tv) tv.click();
    }""")
    await asyncio.sleep(2.0)

    # 2. Select Model A
    await target_page.evaluate("""() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const ma = btns.find(b => (b.innerText || '').trim() === 'Model A');
        if (ma) ma.click();
    }""")
    await asyncio.sleep(1.5)

    # 3. Select LOGS
    await target_page.evaluate("""() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const logs = btns.find(b => (b.innerText || '').trim() === 'LOGS');
        if (logs) logs.click();
    }""")
    await asyncio.sleep(1.5)

    # 4. Click Expand all
    clicked_exp = await target_page.evaluate("""() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const exp = btns.find(b => (b.innerText || '').trim() === 'Expand all');
        if (exp) {
            exp.click();
            return true;
        }
        return false;
    }""")
    print("Clicked Expand all:", clicked_exp)
    await asyncio.sleep(3.0)

    # 5. Expand 'more lines' / 'show more'
    total_expanded = 0
    for round_idx in range(10):
        expanded = await target_page.evaluate("""() => {
            const btns = Array.from(document.querySelectorAll('button')).filter(b => {
                const t = (b.innerText || '').toLowerCase();
                return t.includes('more lines') || t.includes('show more');
            });
            btns.forEach(b => {
                try { b.click(); } catch(e) {}
            });
            return btns.length;
        }""")
        print(f"Round {round_idx}: Clicked {expanded} buttons")
        total_expanded += expanded
        if expanded == 0:
            break
        await asyncio.sleep(2.0)

    print(f"Total expand buttons clicked: {total_expanded}")

    # 6. Extract full innerText
    full_text = await target_page.evaluate('document.body.innerText')
    os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)
    with open(OUT_FILE, 'w', encoding='utf-8') as f:
        f.write(full_text)
    print(f"Successfully saved {OUT_FILE} ({len(full_text)} chars)")

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(extract())
