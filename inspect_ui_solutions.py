import asyncio
import json
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_08ccf272669347c3af63de71b2ecb5e5'
TASK_DIR = os.path.join(r'c:\desarrollo\nueva-mercor', f'task_{TASK_ID}')

async def inspect_ui_solutions():
    p = await async_playwright().start()
    b = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [pg for pg in b.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url][0]

    for model, label in [('model_a', '1 · Agent solution A'), ('model_b', '1 · Agent solution B')]:
        print(f"\nClicking {label} in sidebar...")
        await page.evaluate('''(lbl) => {
            const btns = Array.from(document.querySelectorAll('button, div, span'));
            const tab = btns.find(b => b.innerText && b.innerText.trim() === lbl);
            if (tab) tab.click();
        }''', label)
        await asyncio.sleep(2.5)

        # Screenshot
        ss_path = os.path.join(TASK_DIR, f'{model}_view.png')
        await page.screenshot(path=ss_path)
        print(f"Saved {ss_path}")

        # Extract text in middle pane
        text = await page.evaluate('''() => {
            const middle = document.querySelector('main') || document.body;
            return middle.innerText;
        }''')
        with open(os.path.join(TASK_DIR, f'{model}_pane_text.txt'), 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"Saved {model}_pane_text.txt ({len(text)} chars)")

    await b.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(inspect_ui_solutions())
