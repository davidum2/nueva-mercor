import asyncio
import json
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_08ccf272669347c3af63de71b2ecb5e5'
TASK_DIR = os.path.join(r'c:\desarrollo\nueva-mercor', f'task_{TASK_ID}')

async def main():
    p = await async_playwright().start()
    b = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [pg for pg in b.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url][0]

    # Click Task bundle tab
    await page.evaluate("""() => {
        const btns = Array.from(document.querySelectorAll('button, div, span'));
        const tab = btns.find(b => b.innerText && b.innerText.trim() === 'Task bundle');
        if (tab) tab.click();
    }""")
    await asyncio.sleep(2)

    # Click golden.patch
    await page.evaluate("""() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const btn = btns.find(b => b.innerText && b.innerText.trim() === 'golden.patch');
        if (btn) btn.click();
    }""")
    await asyncio.sleep(2)

    # Inspect code viewer
    res = await page.evaluate("""() => {
        // Look for line numbers or code lines
        const lines = Array.from(document.querySelectorAll('.view-lines, [role="code"], pre, code, .monaco-editor, .cm-content'));
        if (lines.length > 0) {
            return {
                type: 'editor',
                linesCount: lines.length,
                text: lines[0].innerText.substring(0, 1500)
            };
        }
        // Fallback: look for pre or general text container
        const allPre = Array.from(document.querySelectorAll('pre'));
        if (allPre.length > 0) {
            return {
                type: 'pre',
                count: allPre.length,
                text: allPre[allPre.length - 1].innerText.substring(0, 1500)
            };
        }
        return { type: 'none' };
    }""")
    print("Bundle viewer result:", res)

    # Screenshot bundle view
    ss_path = os.path.join(TASK_DIR, 'bundle_view.png')
    await page.screenshot(path=ss_path)
    print(f"Saved {ss_path}")

    await b.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(main())
