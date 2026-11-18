import asyncio
import json
from playwright.async_api import async_playwright

async def inspect():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    ctx = browser.contexts[0]
    rubric_page = [pg for pg in ctx.pages if 'task_a6c04444' in pg.url and '/rubric/' in pg.url][0]

    # Switch back to Spreadsheet view if in Structured
    await rubric_page.evaluate('''() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const sp = btns.find(b => (b.innerText || '').trim() === 'Spreadsheet');
        if (sp) sp.click();
    }''')
    await asyncio.sleep(2.0)

    # Inspect the DOM of the spreadsheet container
    container_info = await rubric_page.evaluate('''() => {
        // Find element containing 'This rubric has no criteria yet'
        const el = Array.from(document.querySelectorAll('*')).find(e => (e.innerText || '').includes('This rubric has no criteria yet'));
        if (!el) return { error: 'Empty criteria message not found' };

        return {
            tag: el.tagName,
            className: el.className,
            parentTag: el.parentElement ? el.parentElement.tagName : null,
            parentClass: el.parentElement ? el.parentElement.className : null,
            parentHTML: el.parentElement ? el.parentElement.outerHTML.slice(0, 300) : null
        };
    }''')

    print("Container Info:", json.dumps(container_info, indent=2))

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(inspect())
