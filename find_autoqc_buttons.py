import asyncio
import json
from playwright.async_api import async_playwright

TASK_ID = 'task_08ccf272669347c3af63de71b2ecb5e5'

async def find_autoqc_elements():
    p = await async_playwright().start()
    b = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [pg for pg in b.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url][0]

    # Inspect all elements in document that mention AutoQC
    elements = await page.evaluate('''() => {
        const all = Array.from(document.querySelectorAll('*'));
        const matches = all.filter(el => {
            const t = (el.innerText || '');
            return (t.includes('AutoQC') || t.includes('AUTOQC')) && t.length < 100;
        });
        return matches.map(el => ({
            tag: el.tagName,
            text: el.innerText.trim(),
            role: el.getAttribute('role'),
            className: el.className
        }));
    }''')
    print('AutoQC matches in DOM:', len(elements))
    for m in elements:
        print(f"[{m['tag']}] role={m['role']} text='{m['text']}' class='{m['className'][:40]}'")

    # Also list all buttons on the page
    buttons = await page.evaluate('''() => {
        return Array.from(document.querySelectorAll('button')).map(b => b.innerText.trim()).filter(t => t.length > 0 && t.length < 60);
    }''')
    print('\nAll buttons on page:', len(buttons))
    for b_text in sorted(set(buttons)):
        print('  Button:', b_text)

    await b.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(find_autoqc_elements())
