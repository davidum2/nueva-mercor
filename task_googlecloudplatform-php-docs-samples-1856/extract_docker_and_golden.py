import asyncio
import os
from playwright.async_api import async_playwright

TASK_ID = "task_a6c044440a2b440a9d578ad5c375ad94"
DEST_DIR = os.path.join(r"c:\desarrollo\nueva-mercor", TASK_ID)
BUNDLE_DIR = os.path.join(DEST_DIR, "bundle")

async def extract_docker_and_golden():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = browser.contexts[0].pages[0]

    # 1. Expand environment folder
    print("Expanding environment...")
    await page.evaluate("""() => {
        const spans = Array.from(document.querySelectorAll('span'));
        const env = spans.find(s => s.innerText.trim() === 'environment');
        if (env) (env.closest('button') || env).click();
    }""")
    await asyncio.sleep(1.0)

    # Click Dockerfile
    print("Clicking Dockerfile...")
    await page.evaluate("""() => {
        const spans = Array.from(document.querySelectorAll('span, button'));
        const df = spans.find(s => s.innerText.trim() === 'Dockerfile');
        if (df) (df.closest('button') || df).click();
    }""")
    await asyncio.sleep(1.5)

    df_content = await page.evaluate("""() => {
        if (window.monaco && window.monaco.editor) {
            const models = window.monaco.editor.getModels();
            // Find model ending with Dockerfile or latest
            for (let i = models.length - 1; i >= 0; i--) {
                const uri = models[i].uri.toString();
                if (uri.includes('Dockerfile')) return models[i].getValue();
            }
            return models[models.length - 1].getValue();
        }
        return null;
    }""")
    if df_content and not df_content.startswith('schema_version'):
        with open(os.path.join(BUNDLE_DIR, "Dockerfile"), "w", encoding="utf-8") as f:
            f.write(df_content)
        print(f"Saved Dockerfile ({len(df_content)} bytes)")
    else:
        print("Dockerfile content unexpected:", df_content[:100] if df_content else None)

    # 2. Expand solution folder
    print("Expanding solution...")
    await page.evaluate("""() => {
        const spans = Array.from(document.querySelectorAll('span'));
        const sol = spans.find(s => s.innerText.trim() === 'solution');
        if (sol) (sol.closest('button') || sol).click();
    }""")
    await asyncio.sleep(1.0)

    # Click golden.patch
    print("Clicking golden.patch...")
    await page.evaluate("""() => {
        const spans = Array.from(document.querySelectorAll('span, button'));
        const gp = spans.find(s => s.innerText.trim() === 'golden.patch');
        if (gp) (gp.closest('button') || gp).click();
    }""")
    await asyncio.sleep(1.5)

    gp_content = await page.evaluate("""() => {
        if (window.monaco && window.monaco.editor) {
            const models = window.monaco.editor.getModels();
            for (let i = models.length - 1; i >= 0; i--) {
                const uri = models[i].uri.toString();
                if (uri.includes('golden.patch')) return models[i].getValue();
            }
            return models[models.length - 1].getValue();
        }
        return null;
    }""")
    if gp_content and not gp_content.startswith('schema_version'):
        with open(os.path.join(BUNDLE_DIR, "golden.patch"), "w", encoding="utf-8") as f:
            f.write(gp_content)
        print(f"Saved golden.patch ({len(gp_content)} bytes)")
    else:
        print("golden.patch content unexpected:", gp_content[:100] if gp_content else None)

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(extract_docker_and_golden())
