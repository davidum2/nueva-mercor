import asyncio
import json
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def check():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    # Expand Deliverable AutoQC
    await page.evaluate("""() => {
        // Find DELIVERABLE AUTOQC header
        const header = Array.from(document.querySelectorAll('div, button')).find(el => el.innerText && el.innerText.trim() === 'DELIVERABLE AUTOQC');
        if (header) {
            header.click();
        }
    }""")
    await asyncio.sleep(2)

    # Dump all text inside DELIVERABLE AUTOQC container
    details = await page.evaluate("""() => {
        // Look for the DELIVERABLE AUTOQC card/container
        const allText = document.body.innerText;
        const autoqcIdx = allText.indexOf('DELIVERABLE AUTOQC');
        
        // Find all run options in dropdown if any
        const runButtons = Array.from(document.querySelectorAll('button')).map(b => b.innerText ? b.innerText.trim() : '').filter(t => t.includes('run') || t.includes('Run') || t.includes('AutoQC'));

        // Find all cards with test names or issues
        const issueCards = [];
        document.querySelectorAll('div').forEach(d => {
            const t = d.innerText || '';
            if ((t.includes('Finding #') || t.includes('issue') || t.includes('passed')) && t.length < 500) {
                issueCards.push(t);
            }
        });

        return {
            runButtons,
            textAroundAutoqc: autoqcIdx !== -1 ? allText.substring(autoqcIdx, autoqcIdx + 3000) : 'NOT FOUND',
            issueCards: Array.from(new Set(issueCards))
        };
    }""")

    print("Run buttons found:", details['runButtons'])
    print("\nText around AutoQC:\n", details['textAroundAutoqc'][:1500])
    print("\nIssue cards:\n", json.dumps(details['issueCards'], indent=2))

    await page.screenshot(path='autoqc_open_view.png')
    print("Saved autoqc_open_view.png")

    await p.stop()

if __name__ == '__main__':
    asyncio.run(check())
