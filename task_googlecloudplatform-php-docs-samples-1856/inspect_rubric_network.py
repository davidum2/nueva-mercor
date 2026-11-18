import asyncio
import json
from playwright.async_api import async_playwright

async def inspect():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    ctx = browser.contexts[0]
    rubric_page = [pg for pg in ctx.pages if 'task_a6c04444' in pg.url and '/rubric/' in pg.url][0]

    # Inspect React components and state on rubric page
    res = await rubric_page.evaluate('''() => {
        // Find elements with React Fiber
        const all = Array.from(document.querySelectorAll('*'));
        function findFiber(el) {
            const k = Object.keys(el).find(key => key.startsWith('__reactFiber$'));
            return k ? el[k] : null;
        }

        let rubricProps = null;
        for (let el of all) {
            const f = findFiber(el);
            if (!f) continue;
            let curr = f;
            let depth = 0;
            while (curr && depth < 20) {
                const props = curr.memoizedProps;
                if (props && (props.rubrics || props.rubric || props.criteria || props.items || props.onAddRow || props.addRow)) {
                    rubricProps = {
                        keys: Object.keys(props),
                        hasRubrics: !!props.rubrics,
                        hasCriteria: !!props.criteria,
                        hasAddRow: !!(props.onAddRow || props.addRow)
                    };
                    break;
                }
                curr = curr.return;
                depth++;
            }
            if (rubricProps) break;
        }

        // Also check if there's any API endpoint or window state
        return {
            rubricProps,
            url: window.location.href,
            storageKeys: Object.keys(localStorage)
        };
    }''')

    print("Rubric Page React Fiber / State:")
    print(json.dumps(res, indent=2))

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(inspect())
