import asyncio
import json
from playwright.async_api import async_playwright

async def run():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    mercor_page = None
    for ctx in browser.contexts:
        for page in ctx.pages:
            if 'mercor.com' in page.url:
                mercor_page = page
                break
        if mercor_page:
            break

    nav_items = await mercor_page.evaluate("""() => {
        const sidebar = Array.from(document.querySelectorAll('aside, nav, [data-slot="sidebar"], [class*="sidebar"]'));
        const buttons = Array.from(document.querySelectorAll('button, a')).map(b => ({
            text: (b.innerText || '').trim().split('\\n').join(' '),
            tag: b.tagName,
            href: b.getAttribute('href')
        })).filter(b => b.text && b.text.length < 50 && (
            b.text.includes('Score') || b.text.includes('Rubric') || b.text.includes('rollout') || b.text.includes('Solution') || b.text.includes('Agent') || b.text.includes('Tab')
        ));
        return { buttons };
    }""")

    print(json.dumps(nav_items, indent=2))

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
