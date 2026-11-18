import asyncio
import json
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_08ccf272669347c3af63de71b2ecb5e5'
TASK_DIR = os.path.join(r'c:\desarrollo\nueva-mercor', f'task_{TASK_ID}')

async def inspect_header():
    p = await async_playwright().start()
    b = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [pg for pg in b.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url][0]

    # Click 1 · Agent solution A
    await page.evaluate('''() => {
        const btns = Array.from(document.querySelectorAll('button, div, span'));
        const tab = btns.find(b => b.innerText && b.innerText.trim() === '1 · Agent solution A');
        if (tab) tab.click();
    }''')
    await asyncio.sleep(2)

    # Let's inspect the header elements containing TRAJECTORY A
    elements = await page.evaluate('''() => {
        const all = Array.from(document.querySelectorAll('*')).filter(el => {
            const t = el.innerText || '';
            return t.includes('AGENT SOLUTION A') || t.includes('TRAJECTORY A');
        });
        return elements = all.slice(0, 10).map(el => ({
            tag: el.tagName,
            cls: el.className,
            text: el.innerText.substring(0, 60),
            role: el.getAttribute('role')
        }));
    }''')
    print("Found elements:", elements)

    # Click the chevron or dropdown near TRAJECTORY A
    clicked = await page.evaluate('''() => {
        const btns = Array.from(document.querySelectorAll('button, [role="button"], svg, div')).filter(el => {
            const t = el.innerText || '';
            return t.includes('TRAJECTORY A') || t.includes('AGENT SOLUTION A');
        });
        if (btns.length > 0) {
            btns[0].click();
            return { ok: true, tag: btns[0].tagName, text: btns[0].innerText };
        }
        return { ok: false };
    }''')
    print("Clicked result:", clicked)
    await asyncio.sleep(2)

    ss_path = os.path.join(TASK_DIR, 'after_trajectory_click.png')
    await page.screenshot(path=ss_path)
    print(f"Saved {ss_path}")

    await b.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(inspect_header())
