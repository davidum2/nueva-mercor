import asyncio
import json
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_08ccf272669347c3af63de71b2ecb5e5'
TASK_DIR = os.path.join(r'c:\desarrollo\nueva-mercor', f'task_{TASK_ID}')

async def inspect_trajectories():
    p = await async_playwright().start()
    b = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [pg for pg in b.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url][0]

    for model, label in [('model_a', '1 · Agent solution A'), ('model_b', '1 · Agent solution B')]:
        print(f"\n--- Checking {label} ---")
        await page.evaluate('''(lbl) => {
            const btns = Array.from(document.querySelectorAll('button, div, span'));
            const tab = btns.find(b => b.innerText && b.innerText.trim() === lbl);
            if (tab) tab.click();
        }''', label)
        await asyncio.sleep(2)

        # Click LOGS button
        print(f"Clicking LOGS for {model}...")
        await page.evaluate('''() => {
            const btns = Array.from(document.querySelectorAll('button'));
            const logBtn = btns.find(b => b.innerText && b.innerText.trim() === 'LOGS');
            if (logBtn) logBtn.click();
        }''')
        await asyncio.sleep(1.5)

        logs = await page.evaluate('''() => {
            const body = document.body.innerText;
            return body.substring(0, 15000);
        }''')
        with open(os.path.join(TASK_DIR, f'{model}_logs.txt'), 'w', encoding='utf-8') as f:
            f.write(logs)
        print(f"Saved {model}_logs.txt ({len(logs)} chars)")

    await b.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(inspect_trajectories())
