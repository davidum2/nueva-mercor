import asyncio
import json
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_f5ba2eb1464a4db2831f60a63283341d'

async def inspect_traj_dom():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    # Select Trajectory Viewer -> Model A -> LOGS
    await page.evaluate("""() => {
        const btns = Array.from(document.querySelectorAll('button, div, [role="tab"]'));
        const tv = btns.find(b => (b.innerText || '').trim() === 'Trajectory Viewer');
        if (tv) tv.click();
    }""")
    await asyncio.sleep(1.0)
    await page.evaluate("""() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const m = btns.find(b => (b.innerText || '').trim() === 'Model A');
        if (m) m.click();
    }""")
    await asyncio.sleep(1.0)
    await page.evaluate("""() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const l = btns.find(b => (b.innerText || '').trim() === 'LOGS');
        if (l) l.click();
    }""")
    await asyncio.sleep(1.5)

    dom_info = await page.evaluate("""() => {
        // Inspect all buttons, headers, and steps
        const btns = Array.from(document.querySelectorAll('button')).map(b => b.innerText ? b.innerText.trim() : '').filter(t => t);
        const headers = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, h6')).map(h => h.innerText.trim());
        
        // Check for step elements
        const stepEls = Array.from(document.querySelectorAll('*')).filter(el => {
            const t = el.innerText || '';
            return t.startsWith('Step ') && t.length < 30 && el.children.length === 0;
        }).map(el => el.innerText.trim());

        // Check if there is an iframe or monaco or pre
        const pres = Array.from(document.querySelectorAll('pre, code')).length;

        return {
            buttons: Array.from(new Set(btns)),
            stepEls: stepEls,
            presCount: pres
        };
    }""")

    print("DOM info under LOGS:")
    print(json.dumps(dom_info, indent=2))

    await page.screenshot(path='task_task_f5ba2eb1464a4db2831f60a63283341d/logs_view.png')
    print("Saved logs_view.png")

    await p.stop()

if __name__ == '__main__':
    asyncio.run(inspect_traj_dom())
