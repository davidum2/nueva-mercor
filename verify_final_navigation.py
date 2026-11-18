import asyncio
import json
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_f5ba2eb1464a4db2831f60a63283341d'
TASK_DIR = os.path.join(r'c:\desarrollo\nueva-mercor', f'task_{TASK_ID}')

async def main():
    p = await async_playwright().start()
    b = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [pg for pg in b.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url][0]

    # 1. Click Navigation in sidebar
    print("Clicking Navigation in sidebar...")
    await page.evaluate('''() => {
        const btns = Array.from(document.querySelectorAll('button, div, span'));
        const nav = btns.find(b => b.innerText && b.innerText.trim() === 'Navigation');
        if (nav) nav.click();
    }''')
    await asyncio.sleep(2)

    # 2. Extract checklist items
    items = await page.evaluate('''() => {
        const navHeader = Array.from(document.querySelectorAll('*')).find(el => el.innerText && el.innerText.trim() === 'Before you submit');
        if (!navHeader) return [{ error: "Before you submit header not found" }];

        const listContainer = navHeader.parentElement;
        const listItems = Array.from(listContainer.querySelectorAll('li, div, [role="listitem"]')).filter(el => {
            const t = el.innerText || '';
            return t.includes('Length limits') || t.includes('AutoQC') || t.includes('Submit');
        });

        return listItems.map(el => {
            const svgs = Array.from(el.querySelectorAll('svg')).map(s => s.className.baseVal || s.getAttribute('class'));
            const text = el.innerText.trim().split('\\n')[0];
            const isGreen = el.innerHTML.includes('text-green') || el.innerHTML.includes('lucide-check') || el.className.includes('green') || svgs.some(c => c && (c.includes('green') || c.includes('check')));
            const isRed = el.innerHTML.includes('text-red') || el.innerHTML.includes('destructive') || svgs.some(c => c && (c.includes('red') || c.includes('alert')));
            return { text, isGreen, isRed };
        });
    }''')

    print("=== CHECKLIST STATUS ===")
    all_green = True
    for it in items:
        if 'error' in it:
            print("ERROR:", it['error'])
            all_green = False
            continue
        status = "GREEN" if it.get('isGreen') else ("RED" if it.get('isRed') else "GRAY")
        if not it.get('isGreen'):
            all_green = False
        print(f"[{status}] {it.get('text')}")

    print(f"\nALL CHECKLIST ITEMS GREEN: {all_green}")

    # Take screenshot of page
    ss_path = os.path.join(TASK_DIR, 'navigation_checklist_final_proof.png')
    await page.screenshot(path=ss_path)
    print("Screenshot saved to:", ss_path)

    # Also inspect AutoQC text in the page
    print("\nClicking Deliverable AutoQC to inspect summary numbers...")
    await page.evaluate('''() => {
        const btns = Array.from(document.querySelectorAll('button, div, span'));
        const tab = btns.find(b => b.innerText && b.innerText.trim() === 'Deliverable AutoQC');
        if (tab) tab.click();
    }''')
    await asyncio.sleep(2)

    autoqc_info = await page.evaluate('''() => {
        const body = document.body.innerText;
        const autoqcIdx = body.indexOf('DELIVERABLE AUTOQC');
        return autoqcIdx !== -1 ? body.substring(autoqcIdx, autoqcIdx + 1000) : body.substring(0, 1000);
    }''')
    print("=== AUTOQC SNIPPET ===")
    print(autoqc_info)

    ss_autoqc = os.path.join(TASK_DIR, 'autoqc_tab_final_proof.png')
    await page.screenshot(path=ss_autoqc)
    print("AutoQC Screenshot saved to:", ss_autoqc)

    await b.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(main())
