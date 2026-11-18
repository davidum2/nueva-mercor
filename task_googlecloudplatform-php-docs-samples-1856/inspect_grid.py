import asyncio
import json
from playwright.async_api import async_playwright

async def inspect():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    ctx = browser.contexts[0]
    rubric_page = [pg for pg in ctx.pages if 'task_a6c04444' in pg.url and '/rubric/' in pg.url][0]

    grid_info = await rubric_page.evaluate('''() => {
        // Look for canvas, grid, table, or contenteditable
        const canvas = Array.from(document.querySelectorAll('canvas')).length;
        const grid = Array.from(document.querySelectorAll('[role="grid"], [role="treegrid"], .handsontable, .ag-root, .rdg')).map(el => el.className);
        const dataCells = Array.from(document.querySelectorAll('[data-cell], [data-col], [data-row]')).map(c => ({
            tag: c.tagName,
            dataCell: c.getAttribute('data-cell'),
            dataRow: c.getAttribute('data-row'),
            dataCol: c.getAttribute('data-col'),
            text: (c.innerText || '').slice(0, 50)
        }));
        
        // Find elements with click handlers or keyboard focus
        const focusable = Array.from(document.querySelectorAll('[tabindex]')).map(el => ({
            tag: el.tagName,
            tabindex: el.getAttribute('tabindex'),
            className: el.className,
            text: (el.innerText || '').slice(0, 50)
        }));

        return { canvas, grid, dataCellsCount: dataCells.length, dataCells: dataCells.slice(0, 10), focusable };
    }''')

    with open('grid_inspect.json', 'w', encoding='utf-8') as f:
        json.dump(grid_info, f, indent=2, ensure_ascii=False)

    print("Grid info written to grid_inspect.json:")
    print("Canvas count:", grid_info['canvas'])
    print("Grid containers:", grid_info['grid'])
    print("Data cells count:", grid_info['dataCellsCount'])
    print("Focusable count:", len(grid_info['focusable']))
    for foc in grid_info['focusable']:
        print(f"  [{foc['tag']}] tabindex={foc['tabindex']} class={foc['className'][:40]}")

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(inspect())
