import asyncio
from playwright.async_api import async_playwright

async def inspect():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    ctx = browser.contexts[0]
    task_page = [pg for pg in ctx.pages if 'task_a6c04444' in pg.url and '/rubric/' not in pg.url and 'sign-in' not in pg.url][0]

    # Click Rubric tab on the main task page
    print("Navigating to Rubric tab on main task page...")
    tab = task_page.locator('button, li').filter(has_text="Rubric (create)").first
    await tab.click()
    await asyncio.sleep(2.0)

    # Inspect all elements under the rubric section
    info = await task_page.evaluate('''() => {
        // Find element with text 'Write 8 to 15 binary questions'
        const el = Array.from(document.querySelectorAll('*')).find(e => (e.innerText || '').includes('Write 8 to 15 binary questions'));
        if (!el) return { error: 'Rubric header not found' };
        
        let container = el.parentElement;
        while (container && container.parentElement && !container.className.includes('space-y') && container.children.length < 3) {
            container = container.parentElement;
        }

        const buttons = Array.from(container.querySelectorAll('button')).map(b => (b.innerText || '').trim());
        const iframes = Array.from(container.querySelectorAll('iframe')).map(f => f.src);
        const links = Array.from(container.querySelectorAll('a')).map(a => ({ text: a.innerText, href: a.href }));

        return {
            containerTag: container.tagName,
            containerClass: container.className,
            buttons,
            iframes,
            links,
            textPreview: container.innerText.slice(0, 1000)
        };
    }''')

    print("Rubric Container Info:")
    for k, v in info.items():
        print(f"{k}: {v}")

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(inspect())
