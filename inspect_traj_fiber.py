import asyncio
import json
from playwright.async_api import async_playwright

async def main():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [p for ctx in browser.contexts for p in ctx.pages if 'mercor.com' in p.url][0]

    res = await page.evaluate('''() => {
        const elements = Array.from(document.querySelectorAll('*'));
        function findReactProps(el) {
            const key = Object.keys(el).find(k => k.startsWith('__reactProps$') || k.startsWith('__reactFiber$'));
            return key ? el[key] : null;
        }

        for (let el of elements) {
            const fiber = findReactProps(el);
            if (!fiber) continue;
            let curr = fiber;
            let depth = 0;
            while (curr && depth < 20) {
                const props = curr.memoizedProps || curr;
                if (props && props.trajectory) {
                    // Inspect props.trajectory and props.task
                    const traj = props.trajectory;
                    const result = {
                        trajKeys: Object.keys(traj),
                        taskKeys: props.task ? Object.keys(props.task) : null
                    };
                    // Check if any property in traj has array or object
                    for (let k of Object.keys(traj)) {
                        if (traj[k] && typeof traj[k] === 'object') {
                            result[k] = Array.isArray(traj[k]) ? `Array(${traj[k].length})` : Object.keys(traj[k]);
                        }
                    }
                    return result;
                }
                curr = curr.return;
                depth++;
            }
        }
        return null;
    }''')

    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
