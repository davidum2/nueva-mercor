import asyncio
import json
import os
import sys
import time
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_f5ba2eb1464a4db2831f60a63283341d'
TASK_DIR = os.path.join(r'c:\desarrollo\nueva-mercor', f'task_{TASK_ID}')

async def run():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url][0]

    # Let's inspect the middle pane headers and click DELIVERABLE AUTOQC accordion
    print("Finding DELIVERABLE AUTOQC accordion header...")
    header_info = await page.evaluate('''() => {
        // Find elements whose text starts with or is DELIVERABLE AUTOQC
        const all = Array.from(document.querySelectorAll('*'));
        const matches = all.filter(el => {
            const t = (el.innerText || '').trim();
            return t === 'DELIVERABLE AUTOQC' || t.startsWith('DELIVERABLE AUTOQC');
        });
        return matches.map(m => ({
            tag: m.tagName,
            text: m.innerText.substring(0, 50),
            className: m.className
        }));
    }''')
    print("Matches:", header_info)

    # Click the DELIVERABLE AUTOQC header
    clicked_header = await page.evaluate('''() => {
        const all = Array.from(document.querySelectorAll('button, div, [role="button"], h2, h3, h4, span'));
        // Find the clickable accordion trigger
        const target = all.find(el => {
            const t = (el.innerText || '').trim();
            return t === 'DELIVERABLE AUTOQC' || (t.startsWith('DELIVERABLE AUTOQC') && t.length < 30);
        });
        if (target) {
            target.click();
            return { ok: true, tag: target.tagName, text: target.innerText };
        }
        return { ok: false };
    }''')
    print("Clicked header result:", clicked_header)
    await asyncio.sleep(2)

    # Now look for Run AutoQC or dropdown button
    print("Looking for Run AutoQC button inside expanded accordion...")
    btn_info = await page.evaluate('''() => {
        const btns = Array.from(document.querySelectorAll('button, div, span')).filter(el => {
            const t = (el.innerText || '').trim();
            return t.includes('Run AutoQC') || t.includes('Latest run') || t.includes('run ·');
        });
        return btns.map(b => ({
            tag: b.tagName,
            text: b.innerText.substring(0, 60),
            className: b.className
        }));
    }''')
    print("Found candidate buttons:", btn_info)

    # Click Run AutoQC or dropdown
    click_res = await page.evaluate('''() => {
        const btns = Array.from(document.querySelectorAll('button, div, [role="button"]'));
        const directRun = btns.find(b => b.innerText && b.innerText.trim() === 'Run AutoQC');
        if (directRun) {
            directRun.click();
            return { ok: true, type: 'direct' };
        }

        const dropdown = btns.find(b => b.innerText && (b.innerText.includes('Latest run') || b.innerText.includes('run ·')));
        if (dropdown) {
            dropdown.click();
            return { ok: true, type: 'dropdown' };
        }
        return { ok: false };
    }''')
    print("Click action result:", click_res)
    await asyncio.sleep(1.5)

    if click_res.get('type') == 'dropdown':
        sub_res = await page.evaluate('''() => {
            const all = Array.from(document.querySelectorAll('[role="menuitem"], button, div, span'));
            const target = all.find(el => el.innerText && el.innerText.trim() === 'Run AutoQC');
            if (target) {
                target.click();
                return { ok: true, text: target.innerText };
            }
            return { ok: false };
        }''')
        print("Dropdown Run AutoQC click result:", sub_res)
        await asyncio.sleep(2)

    # Monitor AutoQC
    print("Monitoring AutoQC run...")
    start = time.time()
    for cycle in range(50):
        await asyncio.sleep(4)
        status = await page.evaluate('''() => {
            const text = document.body.innerText;
            const isRunning = text.includes('AutoQC is running') || text.includes('Compiling') || text.includes('Running AutoQC') || text.includes('Analyzing');
            let prog = '';
            const m = text.match(/Analyzing \\d+\\/\\d+/);
            if (m) prog = m[0];
            else if (text.includes('Compiling')) prog = 'Compiling';
            else if (text.includes('Preparing')) prog = 'Preparing';

            const runBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText && (b.innerText.includes('Latest run') || b.innerText.includes('run ·')));
            const runText = runBtn ? runBtn.innerText.trim() : '';

            const passedMatches = text.match(/(\\d+)\\s*passed/i);
            const majorMatches = text.match(/(\\d+)\\s*major/i);
            const minorMatches = text.match(/(\\d+)\\s*minor/i);

            return {
                isRunning,
                prog,
                runText,
                passed: passedMatches ? passedMatches[0] : null,
                major: majorMatches ? majorMatches[0] : null,
                minor: minorMatches ? minorMatches[0] : null
            };
        }''')
        elapsed = int(time.time() - start)
        print(f"[{elapsed}s] isRunning={status['isRunning']} | prog={status['prog']} | run={status['runText']} | passed={status['passed']} | major={status['major']} | minor={status['minor']}")

        if not status['isRunning'] and cycle >= 2:
            print("AutoQC completed!")
            break

    # Save AutoQC screenshot
    ss_autoqc = os.path.join(TASK_DIR, 'autoqc_post_run.png')
    await page.screenshot(path=ss_autoqc)
    print(f"Saved {ss_autoqc}")

    # Now click Navigation tab in left sidebar or middle
    print("Switching back to Navigation checklist...")
    await page.evaluate('''() => {
        const btns = Array.from(document.querySelectorAll('button, div, span'));
        const nav = btns.find(b => b.innerText && b.innerText.trim() === 'Navigation');
        if (nav) nav.click();
    }''')
    await asyncio.sleep(2)

    # Check checklist items
    items = await page.evaluate('''() => {
        const navHeader = Array.from(document.querySelectorAll('*')).find(el => el.innerText && el.innerText.trim() === 'Before you submit');
        if (!navHeader) return [];

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

    print("\n=== FINAL CHECKLIST ITEMS STATUS ===")
    for it in items:
        st = "GREEN" if it.get('isGreen') else ("RED" if it.get('isRed') else "GRAY")
        print(f"[{st}] {it.get('text')}")

    ss_nav = os.path.join(TASK_DIR, 'final_navigation_checklist_status.png')
    await page.screenshot(path=ss_nav)
    print(f"Saved {ss_nav}")

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
