import asyncio
import json
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def close_and_read():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    if not task_pages:
        print("No task page found!")
        await p.stop()
        return
    page = task_pages[0]

    # Close any overlays/menus
    await page.evaluate("""() => {
        // Remove or close Radix popovers/overlays
        document.querySelectorAll('[data-radix-popper-content-wrapper], [data-radix-focus-guard], [role="menu"], [role="listbox"]').forEach(el => {
            el.remove();
        });
        document.querySelectorAll('div[style*="pointer-events"]').forEach(el => {
            el.style.pointerEvents = 'auto';
        });
    }""")
    await page.keyboard.press("Escape")
    await asyncio.sleep(1)

    # Now inspect AutoQC findings from the page DOM directly without clicking
    findings = await page.evaluate("""() => {
        // Collect text from deliverable autoqc container
        const allText = document.body.innerText;
        
        // Find all cards with 'Finding #'
        const findingEls = Array.from(document.querySelectorAll('*')).filter(el => {
            const t = el.innerText || '';
            return t.includes('Finding #') && el.children.length === 0;
        });

        // Get the issues list
        const issueCards = [];
        document.querySelectorAll('div').forEach(d => {
            const t = d.innerText || '';
            if (t.includes('Finding #') && (t.includes('MINOR') || t.includes('MAJOR'))) {
                // To avoid duplicate parent wrappers, check text length
                if (t.length < 500) {
                    issueCards.push(t);
                }
            }
        });

        // AutoQC summary text
        const autoqcIndex = allText.indexOf('DELIVERABLE AUTOQC');
        const autoqcSnippet = autoqcIndex !== -1 ? allText.substring(autoqcIndex, autoqcIndex + 4000) : '';

        return {
            autoqcSnippet,
            uniqueCards: Array.from(new Set(issueCards))
        };
    }""")

    print("=== AUTOQC SNIPPET ===")
    print(findings['autoqcSnippet'])
    print("=== UNIQUE CARDS ===")
    for c in findings['uniqueCards']:
        print("--- CARD ---")
        print(c)

    await page.screenshot(path='autoqc_no_overlays.png')
    print("Saved autoqc_no_overlays.png")

    await p.stop()

if __name__ == '__main__':
    asyncio.run(close_and_read())
