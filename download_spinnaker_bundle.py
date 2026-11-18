import asyncio
import json
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_08ccf272669347c3af63de71b2ecb5e5'
TASK_DIR = os.path.join(r'c:\desarrollo\nueva-mercor', f'task_{TASK_ID}')
BUNDLE_DIR = os.path.join(TASK_DIR, 'bundle')
os.makedirs(BUNDLE_DIR, exist_ok=True)

async def download_bundle():
    p = await async_playwright().start()
    b = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [pg for pg in b.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url][0]

    # Click Task bundle tab in sidebar
    await page.evaluate('''() => {
        const btns = Array.from(document.querySelectorAll('button, div, span'));
        const tab = btns.find(b => b.innerText && b.innerText.trim() === 'Task bundle');
        if (tab) tab.click();
    }''')
    await asyncio.sleep(2)

    # Let's inspect the bundle file tree and read each file's content
    files = ['Dockerfile', 'golden.patch', 'solve.sh', 'config.json', 'grade.py', 'test.patch', 'test.sh', 'instruction.md']
    
    for filename in files:
        print(f"Extracting {filename}...")
        content = await page.evaluate('''async (fname) => {
            const btns = Array.from(document.querySelectorAll('button'));
            const fbtn = btns.find(b => b.innerText && b.innerText.trim() === fname);
            if (!fbtn) return null;
            fbtn.click();
            // Wait for editor / viewer to update
            await new Promise(r => setTimeout(r, 600));
            // Read code content from pre, code, or editor element
            const pres = Array.from(document.querySelectorAll('pre, code, textarea, [role="code"]'));
            if (pres.length > 0) {
                // Return text from the largest pre/code
                pres.sort((a, b) => (b.innerText || '').length - (a.innerText || '').length);
                return pres[0].innerText;
            }
            return null;
        }''', filename)

        if content:
            with open(os.path.join(BUNDLE_DIR, filename), 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Saved {filename} ({len(content)} chars)")
        else:
            print(f"Could not extract {filename} via click")

    await b.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(download_bundle())
