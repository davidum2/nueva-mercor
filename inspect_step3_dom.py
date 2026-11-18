import asyncio
from playwright.async_api import async_playwright

async def main():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [p for ctx in browser.contexts for p in ctx.pages if 'mercor.com' in p.url][0]

    res = await page.evaluate('''() => {
        // Find element with "ExpandedSpawnLogContextTest.java"
        const all = Array.from(document.querySelectorAll('*'));
        const el = all.find(e => e.children.length === 0 && e.innerText && e.innerText.includes('ExpandedSpawnLogContextTest.java'));
        if (!el) return { error: "not found" };

        let p = el.parentElement;
        return {
            tag: el.tagName,
            text: el.innerText,
            parentTag: p ? p.tagName : null,
            parentText: p ? p.innerText : null,
            parentHTML: p ? p.outerHTML.substring(0, 500) : null
        };
    }''')

    print(res)

if __name__ == "__main__":
    asyncio.run(main())
