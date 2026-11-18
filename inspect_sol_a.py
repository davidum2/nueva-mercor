import asyncio
import json
from playwright.async_api import async_playwright

async def main():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [p for ctx in browser.contexts for p in ctx.pages if 'mercor.com' in p.url][0]

    res = await page.evaluate('''() => {
        // Find element containing "1 • Agent solution A"
        const all = Array.from(document.querySelectorAll('*'));
        const solA = all.find(el => el.innerText && el.innerText.includes('AGENT SOLUTION A') && el.innerText.includes('15 FILES CHANGED'));
        if (!solA) return { error: "solA not found" };

        let parent = solA;
        for (let i = 0; i < 5; i++) {
            if (parent.parentElement) parent = parent.parentElement;
        }

        // Look for buttons, links, or files inside parent
        const buttons = Array.from(parent.querySelectorAll('button, a, [role="button"]')).map(b => ({
            tag: b.tagName,
            text: b.innerText.trim(),
            className: b.className
        }));

        // Check if there are code diffs, files, or pre elements
        const files = Array.from(parent.querySelectorAll('*')).filter(el => {
            const txt = el.innerText?.trim();
            return txt && (txt.endsWith('.java') || txt.endsWith('.proto') || txt.endsWith('.sh') || txt.includes('.patch'));
        }).map(el => el.innerText.trim());

        return {
            buttons,
            files: Array.from(new Set(files))
        };
    }''')

    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
