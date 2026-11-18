import asyncio
import json
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def fast_inspect():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    if not task_pages:
        print("No task page found!")
        await p.stop()
        return
    page = task_pages[0]

    # Expand all via pure JS
    issues = await page.evaluate("""() => {
        // Expand all 'Show more' buttons
        document.querySelectorAll('button').forEach(b => {
            if (b.innerText && b.innerText.includes('Show more')) {
                b.click();
            }
        });

        // Also expand any accordion headers
        document.querySelectorAll('[data-state="closed"]').forEach(el => {
            el.click();
        });

        // Collect all issue elements
        const items = [];
        const headings = Array.from(document.querySelectorAll('h3, h4, div')).filter(el => {
            const t = el.innerText || '';
            return t.includes('8-15 Complete') || t.includes('Score Agrees') || t.includes('Pairwise') || t.includes('Finding #');
        });

        // Get inner text of deliverable AutoQC container
        const container = document.querySelector('div[class*="overflow"]') || document.body;

        return {
            containerText: container.innerText
        };
    }""")

    with open('autoqc_text_dump.txt', 'w', encoding='utf-8') as f:
        f.write(issues['containerText'])

    print("Saved text dump to autoqc_text_dump.txt (length: " + str(len(issues['containerText'])) + ")")

    await page.screenshot(path='autoqc_issues_full.png', full_page=True)
    print("Saved autoqc_issues_full.png")

    await p.stop()

if __name__ == '__main__':
    asyncio.run(fast_inspect())
