import asyncio
import os
import json
from playwright.async_api import async_playwright

TASK_ID = "task_74b080f5a1554daaba2595c070f210f7"
OUTPUT_DIR = os.path.join(os.getcwd(), TASK_ID)

async def extract_models():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [p for ctx in browser.contexts for p in ctx.pages if 'mercor.com' in p.url][0]

    for model_name in ["Model A", "Model B"]:
        folder = os.path.join(OUTPUT_DIR, model_name.lower().replace(" ", "_"))
        os.makedirs(folder, exist_ok=True)
        print(f"\n--- Extrayendo datos para {model_name} ---")

        # Click on Model A / Model B tab
        await page.evaluate(f'''(mName) => {{
            const buttons = Array.from(document.querySelectorAll('button'));
            const b = buttons.find(btn => btn.innerText.trim() === mName);
            if (b) b.click();
        }}''', model_name)
        await asyncio.sleep(1.5)

        # Click all "Show more" buttons if present
        await page.evaluate('''() => {
            const showMores = Array.from(document.querySelectorAll('button')).filter(b => b.innerText.includes('Show more'));
            showMores.forEach(b => b.click());
        }''')
        await asyncio.sleep(0.5)

        # Extract Prompt & Final Answer text
        fa_text = await page.evaluate('''() => {
            // Find FINAL ANSWER heading and sibling/parent text
            const headings = Array.from(document.querySelectorAll('*')).filter(el => el.innerText?.trim() === 'FINAL ANSWER');
            if (headings.length > 0) {
                const parent = headings[0].parentElement;
                return parent ? parent.innerText : '';
            }
            return '';
        }''')
        with open(os.path.join(folder, "final_answer.txt"), "w", encoding="utf-8") as f:
            f.write(fa_text)
        print(f"  -> Final Answer guardado ({len(fa_text)} chars)")

        # Click DIFF tab in trajectory viewer
        await page.evaluate('''() => {
            const buttons = Array.from(document.querySelectorAll('button'));
            const diffBtn = buttons.find(b => b.innerText.trim() === 'DIFF');
            if (diffBtn) diffBtn.click();
        }''')
        await asyncio.sleep(1.5)

        diff_content = await page.evaluate('''() => {
            if (window.monaco && window.monaco.editor) {
                const models = window.monaco.editor.getModels();
                // Return models or diff editor
                const diffEditor = window.monaco.editor.getDiffEditors ? window.monaco.editor.getDiffEditors() : [];
                if (diffEditor.length > 0) {
                    const modified = diffEditor[0].getModel().modified.getValue();
                    const original = diffEditor[0].getModel().original.getValue();
                    return { original, modified };
                }
            }
            const pre = document.querySelector('pre, .monaco-editor');
            return pre ? pre.innerText : '';
        }''')

        with open(os.path.join(folder, "diff.json"), "w", encoding="utf-8") as f:
            json.dump(diff_content, f, indent=2, ensure_ascii=False)
        print(f"  -> Diff guardado")

        # Click LOGS tab in trajectory viewer
        await page.evaluate('''() => {
            const buttons = Array.from(document.querySelectorAll('button'));
            const logsBtn = buttons.find(b => b.innerText.trim() === 'LOGS');
            if (logsBtn) logsBtn.click();
        }''')
        await asyncio.sleep(1.0)

        # Click "Expand all" if available
        await page.evaluate('''() => {
            const btns = Array.from(document.querySelectorAll('button'));
            const expand = btns.find(b => b.innerText.trim() === 'Expand all');
            if (expand) expand.click();
        }''')
        await asyncio.sleep(1.5)

        logs_text = await page.evaluate('''() => {
            // Find container of logs
            const logsContainer = document.querySelector('[role=\"tabpanel\"], .overflow-y-auto');
            return logsContainer ? logsContainer.innerText : document.body.innerText;
        }''')
        with open(os.path.join(folder, "logs_summary.txt"), "w", encoding="utf-8") as f:
            f.write(logs_text)
        print(f"  -> Logs guardados ({len(logs_text)} chars)")

if __name__ == "__main__":
    asyncio.run(extract_models())
