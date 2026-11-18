import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True)

TASK_ID = "task_a6c044440a2b440a9d578ad5c375ad94"

async def check():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if 'rubric' not in pg.url and TASK_ID in pg.url and 'sign-in' not in pg.url]
    if task_pages:
        tpage = task_pages[0]
        # Query all text on the active page
        info = await tpage.evaluate("""() => {
            const tabs = Array.from(document.querySelectorAll('*')).filter(el => el.innerText && el.innerText.includes('Deliverable AutoQC'));
            const autoqcSection = document.querySelector('[data-tab="autoqc"], [class*="autoqc"], main');
            return {
                title: document.title,
                url: window.location.href,
                bodyTextSample: document.body.innerText.slice(0, 1500),
                autoqcFound: !!document.body.innerText.includes('AutoQC')
            };
        }""")
        print("URL:", info['url'])
        print("AutoQC in body:", info['autoqcFound'])
        print("Text sample:\n", info['bodyTextSample'][:600])

    await p.stop()

if __name__ == '__main__':
    asyncio.run(check())
