import asyncio
import json
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_f5ba2eb1464a4db2831f60a63283341d'

async def inspect_autoqc():
    p = await async_playwright().start()
    b = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [pg for pg in b.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url][0]

    # Click Deliverable AutoQC in left sidebar
    await page.evaluate('''() => {
        const btns = Array.from(document.querySelectorAll('button, div, span'));
        const tab = btns.find(b => b.innerText && b.innerText.trim() === 'Deliverable AutoQC');
        if (tab) tab.click();
    }''')
    await asyncio.sleep(2)

    # Extract all text and elements in the middle pane under Deliverable AutoQC
    details = await page.evaluate('''() => {
        const body = document.body.innerText;
        const autoqcIdx = body.indexOf('DELIVERABLE AUTOQC');
        const textSnippet = autoqcIdx !== -1 ? body.substring(autoqcIdx, autoqcIdx + 5000) : body.substring(0, 5000);

        // Find cards or items representing test cases
        const cards = Array.from(document.querySelectorAll('div, li, [role="listitem"]')).filter(el => {
            const t = el.innerText || '';
            return (t.includes('Major') || t.includes('Minor') || t.includes('Passed') || t.includes('Fail') || t.includes('Error')) && t.length < 500;
        }).map(el => el.innerText.trim());

        return {
            textSnippet,
            cards: cards.slice(0, 20)
        };
    }''')

    print("=== AUTOQC SNIPPET ===")
    print(details['textSnippet'])

    print("\n=== CARDS ===")
    for c in set(details['cards']):
        print("--- CARD ---")
        print(c)

    await b.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(inspect_autoqc())
