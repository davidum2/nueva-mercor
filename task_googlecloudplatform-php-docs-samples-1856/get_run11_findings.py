import asyncio
import json
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def get_all_run11_findings():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]
    
    findings = await page.evaluate("""() => {
        // Expand all 'Show more' buttons
        const showMores = Array.from(document.querySelectorAll('button')).filter(b => b.innerText && b.innerText.includes('Show more'));
        for (const sm of showMores) sm.click();

        const issues = [];
        const cardHeaders = Array.from(document.querySelectorAll('div, li, p')).filter(el => {
            const t = el.innerText || '';
            return t.includes('Major issues') || t.includes('Minor issues') || t.includes('Every Rubric') || t.includes('Preference Label') || t.includes('8-15 Complete') || t.includes('Each Rubric Maps') || t.includes('Dimension 3 Actually Audited');
        });

        // Let's get all cards inside AutoQC panel
        const panel = document.querySelector('.py-6') || document.body;
        return panel.innerText;
    }""")

    with open('run11_findings.txt', 'w', encoding='utf-8') as f:
        f.write(findings)

    print("Saved run11_findings.txt. Length:", len(findings))
    await p.stop()

if __name__ == '__main__':
    asyncio.run(get_all_run11_findings())
