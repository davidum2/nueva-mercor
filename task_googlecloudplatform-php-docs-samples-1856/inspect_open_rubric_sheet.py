import asyncio
import json
from playwright.async_api import async_playwright

async def inspect():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    ctx = browser.contexts[0]
    
    # Find Page 6
    rubric_page = None
    for pg in ctx.pages:
        if 'task_a6c04444' in pg.url and '/rubric/' in pg.url:
            rubric_page = pg
            break

    if not rubric_page:
        print("Rubric page not found!")
        await browser.close()
        await p.stop()
        return

    print("Found rubric page:", rubric_page.url)

    # Inspect data-cell or table content
    data = await rubric_page.evaluate('''() => {
        const cells = Array.from(document.querySelectorAll('[data-cell]')).map(c => ({
            cell: c.getAttribute('data-cell'),
            text: (c.innerText || '').trim()
        }));

        // check if handsontable, ag-grid, or table
        const rows = [];
        const table = document.querySelector('table');
        if (table) {
            for (let tr of table.rows) {
                const row = Array.from(tr.cells).map(td => (td.innerText || '').trim().replace('\\n', ' '));
                rows.push(row);
            }
        }

        return {
            cellsCount: cells.length,
            cells: cells.slice(0, 50),
            tableRows: rows.slice(0, 20),
            title: document.title,
            bodySnippet: document.body.innerText.slice(0, 500)
        };
    }''')

    print(f"Title: {data['title']}")
    print(f"Data-cells: {data['cellsCount']}")
    print(f"Table rows count: {len(data['tableRows'])}")
    print("Table rows sample:")
    for r in data['tableRows'][:10]:
        print("  ", r)

    with open('rubric_sheet_inspect.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(inspect())
