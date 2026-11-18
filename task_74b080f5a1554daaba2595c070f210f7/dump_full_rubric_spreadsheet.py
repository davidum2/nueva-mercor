import asyncio
import json
from playwright.async_api import async_playwright

async def run():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    ctx = browser.contexts[0]
    rubric_page = None
    for pg in ctx.pages:
        if '/rubric/' in pg.url:
            rubric_page = pg
            break

    data = await rubric_page.evaluate("""() => {
        const rows = [];
        for (let r = 0; r < 15; r++) {
            const row = {};
            for (let c = 0; c < 9; c++) {
                const cell = document.querySelector(`[data-cell="${r}-${c}"]`);
                row[`col_${c}`] = cell ? cell.innerText.trim() : null;
            }
            rows.push(row);
        }
        return rows;
    }""")

    with open('rubric_spreadsheet_all_15_rows.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("Dumped 15 rows from /rubric/ spreadsheet:")
    for i, r in enumerate(data):
        print(f"Row {i+1}:")
        print(f"  Criteria: {r['col_1'][:60]}")
        print(f"  Dim: {r['col_2']} | Source: {r['col_3']}")
        print(f"  Ans A: {r['col_4']} | Reason A: {r['col_5'][:50]}")
        print(f"  Ans B: {r['col_6']} | Reason B: {r['col_7'][:50]}")

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
