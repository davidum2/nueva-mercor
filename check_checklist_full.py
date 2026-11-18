import asyncio
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_08ccf272669347c3af63de71b2ecb5e5'
TASK_DIR = os.path.join(r'c:\desarrollo\nueva-mercor', f'task_task_{TASK_ID}')

async def check_checklist_full():
    p = await async_playwright().start()
    b = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [pg for pg in b.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url][0]

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

    print(f"=== FULL NAVIGATION CHECKLIST ({len(items)} items) ===")
    red_count = 0
    gray_count = 0
    green_count = 0
    for it in items:
        st = "GREEN" if it.get('isGreen') else ("RED" if it.get('isRed') else "GRAY")
        if st == "RED": red_count += 1
        elif st == "GRAY": gray_count += 1
        else: green_count += 1
        print(f"[{st}] {it.get('text')}")

    print(f"\nSummary: {green_count} GREEN, {red_count} RED, {gray_count} GRAY")

    ss_path = os.path.join(TASK_DIR, 'nav_checklist_detailed.png')
    await page.screenshot(path=ss_path)
    print(f"Saved {ss_path}")

    await b.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(check_checklist_full())
