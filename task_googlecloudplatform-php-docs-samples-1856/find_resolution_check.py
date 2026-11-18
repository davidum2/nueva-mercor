import asyncio
import sys
import re
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def search_js():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    code = await page.evaluate('''() => {
        const scripts = Array.from(document.querySelectorAll('script')).map(s => s.src).filter(Boolean);
        return scripts;
    }''')

    # Evaluate inside the page context searching functions or objects
    res = await page.evaluate('''() => {
        // Search window or webpack chunks
        let matches = [];
        if (window.__webpack_require__) {
            matches.push("has webpack");
        }
        // Search script tags content or fetch
        return {
            title: document.title
        };
    }''')

    # In playwright, fetch scripts and grep
    script_urls = await page.evaluate('() => Array.from(document.querySelectorAll("script[src]")).map(s => s.src)')
    print(f"Total script URLs: {len(script_urls)}")
    
    for url in script_urls:
        if 'chunk' in url or 'app' in url or 'main' in url or 'page' in url:
            try:
                content = await page.evaluate(f'async (u) => {{ const r = await fetch(u); return await r.text(); }}', url)
                if 'autoqc_resolution_required' in content:
                    print(f"Found match in {url}!")
                    idx = content.find('autoqc_resolution_required')
                    snippet = content[max(0, idx - 300):min(len(content), idx + 700)]
                    print("=== SNIPPET ===")
                    print(snippet)
                    print("===============")
            except Exception as e:
                pass

    await p.stop()

if __name__ == '__main__':
    asyncio.run(search_js())
