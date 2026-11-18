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

async def dump_all():
    p = await async_playwright().start()
    b = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [pg for pg in b.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url][0]

    # Click Task bundle tab
    await page.evaluate('''() => {
        const btns = Array.from(document.querySelectorAll('button, div, span'));
        const tab = btns.find(b => b.innerText && b.innerText.trim() === 'Task bundle');
        if (tab) tab.click();
    }''')
    await asyncio.sleep(2)

    # Click every tree item in Explorer to load it into Monaco
    file_names = ['Dockerfile', 'golden.patch', 'solve.sh', 'config.json', 'grade.py', 'test.patch', 'test.sh', 'instruction.md', 'task.toml']
    for fn in file_names:
        clicked = await page.evaluate('''(fn) => {
            const btns = Array.from(document.querySelectorAll('button, div, span'));
            const target = btns.find(b => (b.innerText || '').trim() === fn);
            if (target) {
                target.click();
                return true;
            }
            return false;
        }''', fn)
        print(f"Clicked {fn}: {clicked}")
        await asyncio.sleep(0.8)

    # Now dump all monaco models
    models = await page.evaluate('''() => {
        if (!window.monaco) return [];
        return window.monaco.editor.getModels().map(m => ({
            uri: m.uri.toString(),
            val: m.getValue()
        }));
    }''')

    for m in models:
        uri = m['uri']
        val = m['val']
        # Extract filename
        basename = os.path.basename(uri.replace('\\', '/'))
        target_path = os.path.join(BUNDLE_DIR, basename)
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(val)
        print(f"Saved {basename} ({len(val)} chars) to {target_path}")

    await b.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(dump_all())
