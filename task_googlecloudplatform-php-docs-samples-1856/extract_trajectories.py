import asyncio
import os
from playwright.async_api import async_playwright

TASK_ID = "task_a6c044440a2b440a9d578ad5c375ad94"
DEST_DIR = os.path.join(r"c:\desarrollo\nueva-mercor", TASK_ID)

async def extract_model(page, model_name, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    print(f"\n--- Extracting {model_name} ---")

    # 1. Click Trajectory Viewer
    await page.evaluate("""() => {
        const btns = Array.from(document.querySelectorAll('button, [role="tab"], div'));
        const tv = btns.find(b => (b.innerText || '').trim() === 'Trajectory Viewer');
        if (tv) tv.click();
    }""")
    await asyncio.sleep(1.0)

    # 2. Select Model
    await page.evaluate(f"""() => {{
        const btns = Array.from(document.querySelectorAll('button'));
        const m = btns.find(b => (b.innerText || '').trim() === '{model_name}');
        if (m) m.click();
    }}""")
    await asyncio.sleep(1.0)

    # 3. Select LOGS
    await page.evaluate("""() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const logs = btns.find(b => (b.innerText || '').trim() === 'LOGS');
        if (logs) logs.click();
    }""")
    await asyncio.sleep(1.0)

    # 4. Click Expand all
    clicked_expand = await page.evaluate("""() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const exp = btns.find(b => (b.innerText || '').trim() === 'Expand all');
        if (exp) {
            exp.click();
            return true;
        }
        return false;
    }""")
    print(f"Clicked Expand all for {model_name}: {clicked_expand}")
    await asyncio.sleep(2.0)

    # 5. Expand Show more / more lines
    for round_idx in range(6):
        expanded = await page.evaluate("""() => {
            const btns = Array.from(document.querySelectorAll('button')).filter(b => {
                const t = (b.innerText || '').toLowerCase();
                return t.includes('more lines') || t.includes('show more');
            });
            btns.forEach(b => {
                try { b.click(); } catch(e) {}
            });
            return btns.length;
        }""")
        print(f"[{model_name}] Round {round_idx}: Clicked {expanded} 'more' buttons")
        if expanded == 0:
            break
        await asyncio.sleep(1.5)

    # 6. Extract full body innerText
    full_text = await page.evaluate('document.body.innerText')
    out_file = os.path.join(out_dir, "all_steps_expanded.txt")
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(full_text)
    print(f"Saved {out_file} ({len(full_text)} chars)")

async def main():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = browser.contexts[0].pages[0]

    await extract_model(page, "Model A", os.path.join(DEST_DIR, "model_a"))
    await extract_model(page, "Model B", os.path.join(DEST_DIR, "model_b"))

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(main())
