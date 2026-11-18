import asyncio
import json
from playwright.async_api import async_playwright

async def inspect():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    ctx = browser.contexts[0]
    
    # Find Page 7 (task_74b rubric)
    old_rubric = None
    for pg in ctx.pages:
        if 'task_74b' in pg.url and '/rubric/' in pg.url:
            old_rubric = pg
            break

    if not old_rubric:
        print("Old rubric page not found!")
        await browser.close()
        await p.stop()
        return

    print("Found old rubric page:", old_rubric.url)

    info = await old_rubric.evaluate('''() => {
        const cells = Array.from(document.querySelectorAll('[data-cell]'));
        const firstCell = cells[0];
        let parentHierarchy = [];
        let curr = firstCell;
        while (curr && parentHierarchy.length < 8) {
            parentHierarchy.push({
                tag: curr.tagName,
                className: curr.className,
                id: curr.id
            });
            curr = curr.parentElement;
        }

        return {
            totalDataCells: cells.length,
            sampleCells: cells.slice(0, 10).map(c => ({ cell: c.getAttribute('data-cell'), text: c.innerText })),
            parentHierarchy
        };
    }''')

    print("Old Rubric Info:")
    print("Total data-cells:", info['totalDataCells'])
    print("Parent hierarchy:")
    for h in info['parentHierarchy']:
        print(f"  [{h['tag']}] class={h['className']}")

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(inspect())
