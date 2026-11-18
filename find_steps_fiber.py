import asyncio
import json
from playwright.async_api import async_playwright

async def main():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [p for ctx in browser.contexts for p in ctx.pages if 'mercor.com' in p.url][0]

    res = await page.evaluate('''() => {
        // Find elements with 'Step 1:' or 'Step 108'
        const all = Array.from(document.querySelectorAll('*'));
        const stepEl = all.find(el => el.innerText && el.innerText.includes('Step 1: Calling'));
        if (!stepEl) return { error: "Step 1 not found" };

        function findReactProps(el) {
            const key = Object.keys(el).find(k => k.startsWith('__reactProps$') || k.startsWith('__reactFiber$'));
            return key ? el[key] : null;
        }

        let curr = findReactProps(stepEl);
        let depth = 0;
        let propsFound = [];
        while (curr && depth < 30) {
            const p = curr.memoizedProps || curr;
            if (p) {
                // Check if p has step or item or data
                const keys = Object.keys(p);
                propsFound.push({ depth, keys });
                if (p.step || p.steps || p.items || p.stepData || p.logItem || p.action || p.call) {
                    return {
                        foundKey: true,
                        depth,
                        keys,
                        step: p.step ? Object.keys(p.step) : null,
                        stepsLen: p.steps ? p.steps.length : null,
                        itemsLen: p.items ? p.items.length : null
                    };
                }
            }
            curr = curr.return;
            depth++;
        }
        return { propsFound: propsFound.slice(0, 10) };
    }''')

    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
