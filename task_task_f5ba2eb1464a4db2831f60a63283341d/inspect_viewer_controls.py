import asyncio
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_f5ba2eb1464a4db2831f60a63283341d'

async def inspect_viewer():
    p = await async_playwright().start()
    b = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [pg for pg in b.contexts[0].pages if TASK_ID in pg.url and 'rubric' not in pg.url][0]

    # Click Model A in sidebar
    await page.evaluate('''() => {
        const btns = Array.from(document.querySelectorAll('button, div[role="tab"]'));
        const ma = btns.find(b => (b.innerText || '').trim() === 'Model A');
        if (ma) ma.click();
    }''')
    await asyncio.sleep(1.5)

    info = await page.evaluate('''() => {
        // Find all buttons that contain 'Next' or 'Previous' or numbers
        const btns = Array.from(document.querySelectorAll('button')).map(b => ({
            text: b.innerText ? b.innerText.trim() : '',
            disabled: b.disabled,
            classes: b.className
        }));

        // Find elements with text containing '1 /' or 'Transcript'
        const transEls = Array.from(document.querySelectorAll('*')).filter(el => {
            const t = el.innerText || '';
            return t.includes('Transcript') && el.children.length < 5;
        }).map(el => el.innerText.trim());

        return {
            btns: btns.filter(b => b.text.includes('Next') || b.text.includes('Previous') || b.text.includes('Expand') || b.text.includes('Collapse')),
            transEls
        };
    }''')

    print("Viewer info:")
    print(info)

    await b.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(inspect_viewer())
