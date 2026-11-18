import asyncio
import json
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_08ccf272669347c3af63de71b2ecb5e5'
TASK_DIR = os.path.join(r'c:\desarrollo\nueva-mercor', f'task_{TASK_ID}')

async def inspect_trajectory():
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

    # Click LOGS button
    await page.evaluate('''() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const logBtn = btns.find(b => b.innerText && b.innerText.trim() === 'LOGS');
        if (logBtn) logBtn.click();
    }''')
    await asyncio.sleep(2)

    # Let's inspect all containers under the viewer
    viewer_info = await page.evaluate('''() => {
        const pres = Array.from(document.querySelectorAll('pre, [class*="terminal"], [class*="log"], [class*="step"]'));
        return pres.map(p => ({
            tag: p.tagName,
            cls: p.className,
            len: (p.innerText || '').length,
            snip: (p.innerText || '').substring(0, 300)
        })).filter(x => x.len > 50);
    }''')
    print("Viewer containers:", viewer_info)

    # Let's also check if there are carousel controls (Step 1 of N, Next, Previous)
    carousel_info = await page.evaluate('''() => {
        const all = Array.from(document.querySelectorAll('*'));
        const stepEls = all.filter(el => {
            const t = el.innerText || '';
            return t.includes('Step ') || t.includes('Transcript');
        }).map(el => el.innerText.trim().substring(0, 80));
        return Array.from(new Set(stepEls)).slice(0, 15);
    }''')
    print("Carousel/step indicators:", carousel_info)

    await b.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(inspect_trajectory())
