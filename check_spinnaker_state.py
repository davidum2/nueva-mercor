import asyncio
import json
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_08ccf272669347c3af63de71b2ecb5e5'
TASK_DIR = os.path.join(r'c:\desarrollo\nueva-mercor', f'task_task_{TASK_ID}')

async def inspect_autoqc():
    p = await async_playwright().start()
    b = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [pg for pg in b.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url][0]

    # Click Deliverable AutoQC in sidebar
    await page.evaluate('''() => {
        const btns = Array.from(document.querySelectorAll('button, div, span'));
        const tab = btns.find(b => b.innerText && b.innerText.trim() === 'Deliverable AutoQC');
        if (tab) tab.click();
    }''')
    await asyncio.sleep(2)

    autoqc_text = await page.evaluate('''() => {
        const body = document.body.innerText;
        const autoqcIdx = body.indexOf('DELIVERABLE AUTOQC');
        return autoqcIdx !== -1 ? body.substring(autoqcIdx, autoqcIdx + 4000) : body.substring(0, 4000);
    }''')
    print("=== AUTOQC TEXT ===")
    print(autoqc_text)

    # Click Navigation in sidebar
    await page.evaluate('''() => {
        const btns = Array.from(document.querySelectorAll('button, div, span'));
        const tab = btns.find(b => b.innerText && b.innerText.trim() === 'Navigation');
        if (tab) tab.click();
    }''')
    await asyncio.sleep(2)

    nav_text = await page.evaluate('''() => {
        const body = document.body.innerText;
        const navIdx = body.indexOf('NAVIGATION');
        return navIdx !== -1 ? body.substring(navIdx, navIdx + 2000) : body.substring(0, 2000);
    }''')
    print("\n=== NAVIGATION TEXT ===")
    print(nav_text)

    ss_path = os.path.join(TASK_DIR, 'current_checklist_state.png')
    await page.screenshot(path=ss_path)
    print(f"Saved {ss_path}")

    await b.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(inspect_autoqc())
