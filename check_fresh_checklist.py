import asyncio
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_08ccf272669347c3af63de71b2ecb5e5'
TASK_DIR = os.path.join(r'c:\desarrollo\nueva-mercor', f'task_task_{TASK_ID}')

async def check_fresh_checklist():
    p = await async_playwright().start()
    b = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [pg for pg in b.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url][0]

    print("Reloading page...")
    await page.reload()
    await page.wait_for_load_state('networkidle')
    await asyncio.sleep(3)

    # Click Navigation in sidebar
    await page.evaluate('''() => {
        const btns = Array.from(document.querySelectorAll('button, div, span'));
        const nav = btns.find(b => b.innerText && b.innerText.trim() === 'Navigation');
        if (nav) nav.click();
    }''')
    await asyncio.sleep(2)

    items = await page.evaluate('''() => {
        const navHeader = Array.from(document.querySelectorAll('*')).find(el => el.innerText && el.innerText.trim() === 'Before you submit');
        if (!navHeader) return [];

        const listContainer = navHeader.parentElement;
        const listItems = Array.from(listContainer.querySelectorAll('li, div, [role="listitem"]')).filter(el => {
            const t = el.innerText || '';
            return t.includes('Dimension') || t.includes('Rubric') || t.includes('Task type') || t.includes('Pairwise') || t.includes('Comparative') || t.includes('Length') || t.includes('AutoQC') || t.includes('score') || t.includes('reason') || t.includes('answer');
        });

        return listItems.map(el => {
            const svgs = Array.from(el.querySelectorAll('svg')).map(s => s.className.baseVal || s.getAttribute('class'));
            const text = el.innerText.trim().split('\\n')[0];
            const isGreen = el.innerHTML.includes('text-green') || el.innerHTML.includes('lucide-check') || el.className.includes('green') || svgs.some(c => c && (c.includes('green') || c.includes('check')));
            const isRed = el.innerHTML.includes('text-red') || el.innerHTML.includes('destructive') || svgs.some(c => c && (c.includes('red') || c.includes('alert')));
            return { text, isGreen, isRed };
        });
    }''')

    print(f"\n=== FINAL CHECKLIST POST RELOAD ({len(items)} items) ===")
    green_c = sum(1 for it in items if it.get('isGreen'))
    red_c = sum(1 for it in items if it.get('isRed'))
    gray_c = sum(1 for it in items if not it.get('isGreen') and not it.get('isRed'))
    for it in items:
        st = "GREEN" if it.get('isGreen') else ("RED" if it.get('isRed') else "GRAY")
        print(f"[{st}] {it.get('text')}")
    print(f"\nSummary: {green_c} GREEN, {red_c} RED, {gray_c} GRAY")

    # Check DELIVERABLE AUTOQC accordion test cases pass count
    autoqc_status = await page.evaluate('''() => {
        const text = document.body.innerText;
        const m = text.match(/(\\d+)\\s*\\/\\s*(\\d+)\\s*test cases/i) || text.match(/(\\d+)\\s*passed/i);
        return m ? m[0] : null;
    }''')
    print("AutoQC test cases status:", autoqc_status)

    ss_final = os.path.join(TASK_DIR, 'final_navigation_checklist_100_percent.png')
    await page.screenshot(path=ss_final)
    print(f"Saved {ss_final}")

    await b.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(check_fresh_checklist())
