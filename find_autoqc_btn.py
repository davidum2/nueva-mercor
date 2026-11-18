import asyncio
import json
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_f5ba2eb1464a4db2831f60a63283341d'

async def find_autoqc_button():
    p = await async_playwright().start()
    b = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [pg for pg in b.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url][0]

    # Click Deliverable AutoQC in sidebar
    await page.evaluate('''() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const tab = btns.find(b => b.innerText && b.innerText.trim() === 'Deliverable AutoQC');
        if (tab) tab.click();
    }''')
    await asyncio.sleep(2)

    # Dump all elements in the Deliverable AutoQC panel
    info = await page.evaluate('''() => {
        const btns = Array.from(document.querySelectorAll('button')).map(b => ({
            text: b.innerText ? b.innerText.trim() : '',
            classes: b.className,
            disabled: b.disabled,
            visible: b.offsetParent !== null
        })).filter(b => b.text.length > 0 && b.text.length < 80);

        return {
            buttons: btns
        };
    }''')

    print("Visible buttons:")
    for btn in info['buttons']:
        if any(k in btn['text'].lower() for k in ['run', 'qc', 'auto', 'rerun', 'latest', 'failing']):
            print(" ->", btn)

    await b.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(find_autoqc_button())
