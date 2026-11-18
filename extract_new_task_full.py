import asyncio
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_f5ba2eb1464a4db2831f60a63283341d'
TASK_DIR = os.path.join(r'c:\desarrollo\nueva-mercor', f'task_{TASK_ID}')
BUNDLE_DIR = os.path.join(TASK_DIR, 'bundle')
os.makedirs(BUNDLE_DIR, exist_ok=True)
os.makedirs(os.path.join(TASK_DIR, 'model_a'), exist_ok=True)
os.makedirs(os.path.join(TASK_DIR, 'model_b'), exist_ok=True)

async def extract_task_bundle_and_trajectories():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    if not task_pages:
        print("Task page not found!")
        await p.stop()
        return
    page = task_pages[0]

    # --- 1. EXTRACT REVIEWER FEEDBACK ---
    print("\n--- 1. EXTRACTING REVIEWER FEEDBACK TAB ---")
    await page.evaluate("""() => {
        const btns = Array.from(document.querySelectorAll('button, div[role="tab"]'));
        const rf = btns.find(b => (b.innerText || '').trim() === 'Reviewer Feedback');
        if (rf) rf.click();
    }""")
    await asyncio.sleep(2.0)
    rf_text = await page.evaluate("() => document.body.innerText")
    with open(os.path.join(TASK_DIR, 'reviewer_feedback_tab_text.txt'), 'w', encoding='utf-8') as f:
        f.write(rf_text)
    print(f"Saved reviewer_feedback_tab_text.txt ({len(rf_text)} chars)")
    await page.screenshot(path=os.path.join(TASK_DIR, 'reviewer_feedback_tab.png'))

    # --- 2. EXTRACT TASK BUNDLE ---
    print("\n--- 2. EXTRACTING TASK BUNDLE ---")
    await page.evaluate("""() => {
        const btns = Array.from(document.querySelectorAll('button, div[role="tab"]'));
        const tb = btns.find(b => (b.innerText || '').trim() === 'B · Task bundle' || (b.innerText || '').trim() === 'Task bundle');
        if (tb) tb.click();
    }""")
    await asyncio.sleep(2.0)

    # Find bundle file buttons
    file_names = await page.evaluate("""() => {
        const buttons = Array.from(document.querySelectorAll('button'));
        // Usually file names end with .patch, .md, .py, .sh, .json, .toml, or Dockerfile
        return buttons.map(b => (b.innerText || '').trim()).filter(t => {
            return t.includes('.') || t === 'Dockerfile';
        });
    }""")
    print("Bundle files identified:", file_names)

    for fname in set(file_names):
        if not fname or len(fname) > 50:
            continue
        print(f"Opening bundle file: {fname}...")
        clicked = await page.evaluate(f"""(fn) => {{
            const buttons = Array.from(document.querySelectorAll('button'));
            const target = buttons.find(b => (b.innerText || '').trim() === fn);
            if (target) {{
                target.scrollIntoView({{ block: 'center' }});
                target.click();
                return true;
            }}
            return false;
        }}""", fname)

        if clicked:
            await asyncio.sleep(1.0)
            content = await page.evaluate("""() => {
                if (window.monaco && window.monaco.editor) {
                    const models = window.monaco.editor.getModels();
                    if (models.length > 0) {
                        return models[models.length - 1].getValue();
                    }
                }
                const editorEl = document.querySelector('.monaco-editor');
                if (editorEl) return editorEl.innerText;
                const pre = document.querySelector('pre');
                if (pre) return pre.innerText;
                return null;
            }""")
            if content:
                out_path = os.path.join(BUNDLE_DIR, fname)
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"  -> Saved {fname} ({len(content)} bytes)")
            else:
                print(f"  -> Could not get content for {fname}")

    # --- 3. EXTRACT MODEL A TRAJECTORY ---
    print("\n--- 3. EXTRACTING MODEL A TRAJECTORY ---")
    await page.evaluate("""() => {
        const btns = Array.from(document.querySelectorAll('button, div[role="tab"]'));
        const ma = btns.find(b => (b.innerText || '').trim() === 'Model A');
        if (ma) ma.click();
    }""")
    await asyncio.sleep(2.0)

    # Click Expand all
    await page.evaluate("""() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const exp = btns.find(b => (b.innerText || '').trim() === 'Expand all');
        if (exp) exp.click();
    }""")
    await asyncio.sleep(2.0)

    # Click more lines / show more
    for r in range(12):
        c = await page.evaluate("""() => {
            const btns = Array.from(document.querySelectorAll('button')).filter(b => {
                const t = (b.innerText || '').toLowerCase();
                return t.includes('more lines') || t.includes('show more');
            });
            btns.forEach(b => { try { b.click(); } catch(e) {} });
            return btns.length;
        }""")
        if c == 0:
            break
        await asyncio.sleep(1.5)

    model_a_text = await page.evaluate("() => document.body.innerText")
    out_a = os.path.join(TASK_DIR, 'model_a', 'all_steps_expanded.txt')
    with open(out_a, 'w', encoding='utf-8') as f:
        f.write(model_a_text)
    print(f"Saved Model A trajectory to {out_a} ({len(model_a_text)} chars)")
    await page.screenshot(path=os.path.join(TASK_DIR, 'model_a', 'model_a_screen.png'))

    # --- 4. EXTRACT MODEL B TRAJECTORY ---
    print("\n--- 4. EXTRACTING MODEL B TRAJECTORY ---")
    await page.evaluate("""() => {
        const btns = Array.from(document.querySelectorAll('button, div[role="tab"]'));
        const mb = btns.find(b => (b.innerText || '').trim() === 'Model B');
        if (mb) mb.click();
    }""")
    await asyncio.sleep(2.0)

    # Click Expand all
    await page.evaluate("""() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const exp = btns.find(b => (b.innerText || '').trim() === 'Expand all');
        if (exp) exp.click();
    }""")
    await asyncio.sleep(2.0)

    # Click more lines / show more
    for r in range(12):
        c = await page.evaluate("""() => {
            const btns = Array.from(document.querySelectorAll('button')).filter(b => {
                const t = (b.innerText || '').toLowerCase();
                return t.includes('more lines') || t.includes('show more');
            });
            btns.forEach(b => { try { b.click(); } catch(e) {} });
            return btns.length;
        }""")
        if c == 0:
            break
        await asyncio.sleep(1.5)

    model_b_text = await page.evaluate("() => document.body.innerText")
    out_b = os.path.join(TASK_DIR, 'model_b', 'all_steps_expanded.txt')
    with open(out_b, 'w', encoding='utf-8') as f:
        f.write(model_b_text)
    print(f"Saved Model B trajectory to {out_b} ({len(model_b_text)} chars)")
    await page.screenshot(path=os.path.join(TASK_DIR, 'model_b', 'model_b_screen.png'))

    await p.stop()
    print("\nExtraction finished successfully!")

if __name__ == '__main__':
    asyncio.run(extract_task_bundle_and_trajectories())
