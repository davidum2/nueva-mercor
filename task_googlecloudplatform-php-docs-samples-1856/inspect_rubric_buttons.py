import asyncio
import json
from playwright.async_api import async_playwright

async def inspect():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    ctx = browser.contexts[0]
    
    rubric_page = [pg for pg in ctx.pages if 'task_a6c04444' in pg.url and '/rubric/' in pg.url][0]

    elements_info = await rubric_page.evaluate('''() => {
        const btns = Array.from(document.querySelectorAll('button, a, [role="tab"], [role="button"]')).map(el => ({
            tag: el.tagName,
            text: (el.innerText || '').trim(),
            role: el.getAttribute('role'),
            className: el.className
        }));

        const allText = document.body.innerText;
        return { btns, allText };
    }''')

    print("Buttons found:")
    for b in elements_info['btns']:
        if b['text']:
            print(f"  [{b['tag']}] {b['text']} (role={b['role']})")

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(inspect())
