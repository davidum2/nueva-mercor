import asyncio
import json
from playwright.async_api import async_playwright

async def inspect():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [pg for ctx in browser.contexts for pg in ctx.pages if 'task_a6c04444' in pg.url and 'sign-in' not in pg.url][0]

    # Navigate to Rubric tab
    await page.evaluate('''() => {
        const btns = Array.from(document.querySelectorAll('button, li, [role="tab"]'));
        const rubTab = btns.find(b => (b.innerText || '').trim() === 'Rubric (create)' || (b.innerText || '').trim() === 'Rubric');
        if (rubTab) rubTab.click();
    }''')
    await asyncio.sleep(2.0)

    # Inspect all elements under tab E
    tab_e_info = await page.evaluate('''() => {
        const iframes = Array.from(document.querySelectorAll('iframe')).map(f => f.src);
        const links = Array.from(document.querySelectorAll('a')).map(a => ({ text: a.innerText, href: a.href }));
        const tables = Array.from(document.querySelectorAll('table')).map(t => ({
            rows: t.rows.length,
            text: t.innerText.slice(0, 200)
        }));
        const divs = Array.from(document.querySelectorAll('*')).filter(el => {
            const t = el.innerText || '';
            return t.includes('Google Sheets') || t.includes('Open in New Tab') || t.includes('Spreadsheet');
        }).map(el => ({ tag: el.tagName, text: el.innerText.slice(0, 100) }));

        return { iframes, links, tables, divs: divs.slice(0, 5) };
    }''')

    print(json.dumps(tab_e_info, indent=2))

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(inspect())
