import asyncio
import json
from playwright.async_api import async_playwright

TASK_ID = "task_a6c044440a2b440a9d578ad5c375ad94"
CAMPAIGN_ID = "camp_75099d23386f4394ab7596a5ea538da8"
RUBRIC_URL = f"https://studio.mercor.com/annotator/tasks/{TASK_ID}/rubric/?campaignId={CAMPAIGN_ID}"

async def inspect_rubric():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    ctx = browser.contexts[0]
    
    # Check if there's already a rubric page or open a new one
    rubric_page = await ctx.new_page()
    print(f"Navigating to {RUBRIC_URL}...")
    await rubric_page.goto(RUBRIC_URL)
    await asyncio.sleep(5.0)

    rows = await rubric_page.evaluate("""() => {
        const result = [];
        for (let r = 0; r < 15; r++) {
            const cell0 = document.querySelector(`[data-cell="${r}-0"]`);
            if (!cell0 && r >= 8) break;
            const rowData = { row: r };
            for (let c = 0; c <= 8; c++) {
                const cell = document.querySelector(`[data-cell="${r}-${c}"]`);
                rowData[`col_${c}`] = cell ? cell.innerText.trim() : null;
            }
            result.push(rowData);
        }
        return result;
    }""")

    print(f"Rubric spreadsheet rows ({len(rows)}):")
    for r in rows:
        print(f"Row {r['row']}: Col0={r['col_0']} | Col1={r['col_1'][:50] if r['col_1'] else None} | Col2={r['col_2']} | Col3={r['col_3']} | AnsA={r['col_4']} | AnsB={r['col_6']}")

    with open(f"c:/desarrollo/nueva-mercor/{TASK_ID}/rubric_spreadsheet_dump.json", "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)

    await rubric_page.close()
    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(inspect_rubric())
