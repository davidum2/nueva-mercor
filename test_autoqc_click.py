import asyncio
import json
import os
import sys
import time
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_f5ba2eb1464a4db2831f60a63283341d'
TASK_DIR = os.path.join(r'c:\desarrollo\nueva-mercor', f'task_{TASK_ID}')

async def main():
    p = await async_playwright().start()
    b = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [pg for pg in b.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url][0]

    # Let's find and click the accordion header with cursor-pointer
    print("Clicking the exact cursor-pointer DELIVERABLE AUTOQC element...")
    res = await page.evaluate('''() => {
        const header = Array.from(document.querySelectorAll('div')).find(d => 
            d.className.includes('cursor-pointer') && 
            d.innerText && d.innerText.includes('DELIVERABLE AUTOQC')
        );
        if (header) {
            header.click();
            return { ok: true, class: header.className, text: header.innerText };
        }
        return { ok: false };
    }''')
    print("Click header res:", res)
    await asyncio.sleep(2)

    # Take screenshot of what opened
    ss1 = os.path.join(TASK_DIR, 'opened_accordion.png')
    await page.screenshot(path=ss1)
    print("Saved", ss1)

    # Let's inspect all buttons/clickable elements visible in the middle pane
    buttons = await page.evaluate('''() => {
        const btns = Array.from(document.querySelectorAll('button, [role="button"]'));
        return btns.map(b => ({
            tag: b.tagName,
            text: (b.innerText || '').trim(),
            role: b.getAttribute('role'),
            className: b.className
        })).filter(b => b.text.length > 0 && b.text.length < 50);
    }''')
    print("Buttons found:")
    for btn in buttons:
        print("  -", btn['text'], f"({btn['tag']})")

    await b.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(main())
