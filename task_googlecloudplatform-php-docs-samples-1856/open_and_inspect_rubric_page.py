import asyncio
import json
from playwright.async_api import async_playwright

RUBRIC_URL = "https://studio.mercor.com/annotator/tasks/task_a6c044440a2b440a9d578ad5c375ad94/rubric/?from_view=fcbdb05d-8939-47e2-b16a-bdbe3950c5ea"

async def open_rubric_page():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    ctx = browser.contexts[0]

    # Check if page already open
    rubric_page = None
    for pg in ctx.pages:
        if 'task_a6c04444' in pg.url and '/rubric/' in pg.url:
            rubric_page = pg
            break

    if not rubric_page:
        print("Opening new page for rubric spreadsheet...")
        rubric_page = await ctx.new_page()
        await rubric_page.goto(RUBRIC_URL, wait_until='networkidle')
    else:
        print("Found existing rubric page:", rubric_page.url)

    await asyncio.sleep(3.0)

    # Inspect spreadsheet table
    info = await rubric_page.evaluate('''() => {
        const cells = Array.from(document.querySelectorAll('[data-cell]')).map(c => ({
            cell: c.getAttribute('data-cell'),
            text: (c.innerText || '').trim().slice(0, 100)
        }));
        const tables = Array.from(document.querySelectorAll('table')).length;
        const textareas = Array.from(document.querySelectorAll('textarea')).length;
        const bodyPreview = document.body.innerText.slice(0, 500);

        return {
            cellsCount: cells.length,
            cellsSample: cells.slice(0, 30),
            tables,
            textareas,
            bodyPreview
        };
    }''')

    print("Rubric Page Inspection:")
    print(f"Total data-cell elements: {info['cellsCount']}")
    print("Sample cells:")
    for c in info['cellsSample'][:15]:
        print(f"  {c['cell']}: {c['text']}")

    with open('rubric_spreadsheet_dump.json', 'w', encoding='utf-8') as f:
        json.dump(info, f, indent=2, ensure_ascii=False)

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(open_rubric_page())
