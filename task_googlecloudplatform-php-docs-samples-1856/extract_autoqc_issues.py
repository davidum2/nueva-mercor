import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def get_issues():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]
    
    data = await page.evaluate("""() => {
        // Expand all 'Show more' buttons inside AutoQC
        const showMores = Array.from(document.querySelectorAll('button')).filter(b => b.innerText && b.innerText.includes('Show more'));
        for (const sm of showMores) sm.click();

        const cards = Array.from(document.querySelectorAll('*')).filter(el => {
            const t = el.innerText || '';
            return (t.includes('MAJOR') || t.includes('MINOR') || t.includes('Finding #')) && el.children.length > 1;
        });

        // Get all text inside the AutoQC container
        const container = document.querySelector('div:has(> [class*="border rounded-lg"])') || document.body;
        return {
            containerText: container.innerText
        };
    }""")

    with open('autoqc_full_issues.txt', 'w', encoding='utf-8') as f:
        f.write(data['containerText'])

    print("Saved autoqc_full_issues.txt. Length:", len(data['containerText']))
    await p.stop()

if __name__ == '__main__':
    asyncio.run(get_issues())
