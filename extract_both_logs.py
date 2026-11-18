import asyncio
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_f5ba2eb1464a4db2831f60a63283341d'
TASK_DIR = os.path.join(r'c:\desarrollo\nueva-mercor', f'task_{TASK_ID}')

async def extract_logs_for_side(page, model_name, out_file):
    print(f"\n==========================================")
    print(f"Extracting logs for {model_name}...")
    print(f"==========================================")

    # 1. Click Trajectory Viewer in sidebar or tabs
    await page.evaluate("""() => {
        const btns = Array.from(document.querySelectorAll('button, div, [role="tab"]'));
        const tv = btns.find(b => (b.innerText || '').trim() === 'Trajectory Viewer');
        if (tv) tv.click();
    }""")
    await asyncio.sleep(1.5)

    # 2. Click Model button (Model A or Model B)
    await page.evaluate(f"""() => {{
        const btns = Array.from(document.querySelectorAll('button'));
        const m = btns.find(b => (b.innerText || '').trim() === '{model_name}');
        if (m) m.click();
    }}""")
    await asyncio.sleep(1.5)

    # 3. Click LOGS
    await page.evaluate("""() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const logs = btns.find(b => (b.innerText || '').trim() === 'LOGS');
        if (logs) logs.click();
    }""")
    await asyncio.sleep(1.5)

    # 4. Click Expand all
    expanded_all = await page.evaluate("""() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const exp = btns.find(b => (b.innerText || '').trim() === 'Expand all');
        if (exp) {
            exp.click();
            return true;
        }
        return false;
    }""")
    print(f"Clicked Expand all: {expanded_all}")
    await asyncio.sleep(2.0)

    # 5. Click more lines / show more
    for r in range(12):
        c = await page.evaluate("""() => {
            const btns = Array.from(document.querySelectorAll('button')).filter(b => {
                const t = (b.innerText || '').toLowerCase();
                return t.includes('more lines') || t.includes('show more');
            });
            btns.forEach(b => { try { b.click(); } catch(e) {} });
            return btns.length;
        }""")
        print(f"Round {r+1}: expanded {c} buttons")
        if c == 0:
            break
        await asyncio.sleep(1.5)

    # 6. Extract text from the log viewer container
    log_text = await page.evaluate("""() => {
        // Look for the main log container or article or div with steps
        const containers = Array.from(document.querySelectorAll('div, section, main')).filter(d => {
            const t = d.innerText || '';
            return t.includes('Step 1') && (t.includes('Calling tool') || t.includes('Input:') || t.includes('[Thinking]'));
        });
        if (containers.length > 0) {
            // Find the most specific (shortest text that still has at least 500 chars)
            containers.sort((a, b) => a.innerText.length - b.innerText.length);
            return containers[0].innerText;
        }
        return document.body.innerText;
    }""")

    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(log_text)
    print(f"Saved {out_file} ({len(log_text)} chars)")

async def main():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    if not task_pages:
        print("Task page not found!")
        await p.stop()
        return
    page = task_pages[0]

    await extract_logs_for_side(page, "Model A", os.path.join(TASK_DIR, "model_a", "trajectory_logs.txt"))
    await extract_logs_for_side(page, "Model B", os.path.join(TASK_DIR, "model_b", "trajectory_logs.txt"))

    await p.stop()
    print("\nLogs extraction complete!")

if __name__ == '__main__':
    asyncio.run(main())
