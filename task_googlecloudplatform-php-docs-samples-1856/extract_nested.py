import asyncio
import os
from playwright.async_api import async_playwright

TASK_ID = "task_a6c044440a2b440a9d578ad5c375ad94"
DEST_DIR = os.path.join(r"c:\desarrollo\nueva-mercor", TASK_ID)
BUNDLE_DIR = os.path.join(DEST_DIR, "bundle")

async def extract_nested():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = browser.contexts[0].pages[0]

    # Expand folders if needed
    for folder in ['environment', 'solution', 'tests']:
        await page.evaluate(f"""(f) => {{
            const btns = Array.from(document.querySelectorAll('button, div, span'));
            const b = btns.find(x => (x.innerText || '').trim() === f);
            if (b) b.click();
        }}""", folder)
        await asyncio.sleep(0.5)

    for fname in ['Dockerfile', 'golden.patch']:
        print(f"Clicking {fname}...")
        await page.evaluate(f"""(fn) => {{
            const btns = Array.from(document.querySelectorAll('button'));
            const target = btns.find(b => (b.innerText || '').trim() === fn);
            if (target) {{
                target.scrollIntoView({{ block: 'center' }});
                target.click();
            }}
        }}""", fname)
        await asyncio.sleep(1.5)

        content = await page.evaluate("""() => {
            if (window.monaco && window.monaco.editor) {
                const models = window.monaco.editor.getModels();
                if (models.length > 0) {
                    return models[models.length - 1].getValue();
                }
            }
            return null;
        }""")
        if content:
            out_path = os.path.join(BUNDLE_DIR, fname)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"  -> Saved {fname} ({len(content)} bytes)")
        else:
            print(f"  -> Failed to get {fname}")

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(extract_nested())
