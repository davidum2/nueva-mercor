import asyncio
from playwright.async_api import async_playwright

async def inspect_explorer():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = browser.contexts[0].pages[0]

    tree = await page.evaluate("""() => {
        const els = Array.from(document.querySelectorAll('*')).filter(el => {
            return (el.innerText || '').trim() === 'EXPLORER' && el.children.length === 0;
        });
        if (!els.length) return 'no EXPLORER';
        
        // Find container
        let p = els[0].parentElement;
        while (p && !p.className.includes('tree') && !p.querySelector('[role="tree"]')) {
            p = p.parentElement;
            if (p.tagName === 'BODY') break;
        }

        const items = Array.from((p || document).querySelectorAll('*')).filter(el => {
            const t = (el.innerText || '').trim();
            return ['Dockerfile', 'golden.patch', 'environment', 'solution', 'tests'].includes(t) && el.children.length === 0;
        }).map(el => ({
            tag: el.tagName,
            text: el.innerText.trim(),
            parentTag: el.parentElement.tagName,
            parentClass: el.parentElement.className,
            grandParentClass: el.parentElement.parentElement?.className
        }));

        return { items };
    }""")
    print("Explorer items:", tree)

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(inspect_explorer())
