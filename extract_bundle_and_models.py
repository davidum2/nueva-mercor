import asyncio
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_f5ba2eb1464a4db2831f60a63283341d'
TASK_DIR = os.path.join(r'c:\desarrollo\nueva-mercor', f'task_{TASK_ID}')
BUNDLE_DIR = os.path.join(TASK_DIR, 'bundle')
os.makedirs(BUNDLE_DIR, exist_ok=True)

TARGET_FILES = [
    'golden.patch',
    'solve.sh',
    'instruction.md',
    'task.toml',
    'problem_statement.md',
    'test.patch',
    'test.sh',
    'grade.py',
    'Dockerfile'
]

async def extract_bundle_and_models():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    if not task_pages:
        print("Task page not found!")
        await p.stop()
        return
    page = task_pages[0]

    # --- 1. EXTRACT BUNDLE FILES ---
    print("\n--- EXTRACTING TASK BUNDLE ---")
    await page.evaluate("""() => {
        const btns = Array.from(document.querySelectorAll('button, div[role="tab"]'));
        const tb = btns.find(b => (b.innerText || '').trim() === 'B · Task bundle' || (b.innerText || '').trim() === 'Task bundle');
        if (tb) tb.click();
    }""")
    await asyncio.sleep(2.0)

    for fname in TARGET_FILES:
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
        else:
            print(f"  -> Button for {fname} not found")

    # --- 2. EXTRACT MODEL A TRAJECTORY ---
    print("\n--- EXTRACTING MODEL A TRAJECTORY ---")
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
    for r in range(15):
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

    # --- 3. EXTRACT MODEL B TRAJECTORY ---
    print("\n--- EXTRACTING MODEL B TRAJECTORY ---")
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
    for r in range(15):
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

    await p.stop()
    print("\nExtraction complete!")

if __name__ == '__main__':
    asyncio.run(extract_bundle_and_models())
