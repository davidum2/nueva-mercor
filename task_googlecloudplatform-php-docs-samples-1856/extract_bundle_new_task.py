import asyncio
import os
from playwright.async_api import async_playwright

TASK_ID = "task_a6c044440a2b440a9d578ad5c375ad94"
DEST_DIR = os.path.join(r"c:\desarrollo\nueva-mercor", TASK_ID)
BUNDLE_DIR = os.path.join(DEST_DIR, "bundle")

FILES_TO_EXTRACT = [
    "Dockerfile",
    "golden.patch",
    "solve.sh",
    "config.json",
    "grade.py",
    "test.patch",
    "test.sh",
    "instruction.md",
    "task.toml"
]

async def main():
    os.makedirs(BUNDLE_DIR, exist_ok=True)
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = browser.contexts[0].pages[0]

    # First click tab "B · Task bundle" in sidebar if needed
    await page.evaluate("""() => {
        const els = Array.from(document.querySelectorAll('button, div, [role="tab"]'));
        const tab = els.find(e => (e.innerText || '').trim() === 'B · Task bundle' || (e.innerText || '').trim() === 'Task bundle');
        if (tab) tab.click();
    }""")
    await asyncio.sleep(1.5)

    for fname in FILES_TO_EXTRACT:
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
            if content is not None:
                out_path = os.path.join(BUNDLE_DIR, fname)
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"  -> Saved {fname} ({len(content)} bytes)")
            else:
                print(f"  -> Could not get content for {fname}")
        else:
            print(f"  -> Button for {fname} not found")

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(main())
