import asyncio
from playwright.async_api import async_playwright

async def inspect_page1():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    ctx = browser.contexts[0]
    rubric_page = None
    for pg in ctx.pages:
        if '/rubric/' in pg.url:
            rubric_page = pg
            break

    if not rubric_page:
        print("Rubric page not found!")
        return

    info = await rubric_page.evaluate("""() => {
        const btns = Array.from(document.querySelectorAll('button')).map(b => b.innerText.trim());
        const rows = [];
        for (let r = 0; r < 15; r++) {
            const rowData = {};
            for (let c = 0; c <= 8; c++) {
                const cell = document.querySelector(`[data-cell="${r}-${c}"]`);
                rowData[`col_${c}`] = cell ? cell.innerText.trim() : null;
            }
            rows.push(rowData);
        }
        return {
            title: document.title,
            headerText: document.querySelector('header')?.innerText || '',
            buttons: btns,
            rows: rows
        };
    }""")
    print("Rubric Page Buttons:", info['buttons'])
    print("Header Text:", info['headerText'])
    print("\nRows summary:")
    for idx, r in enumerate(info['rows']):
        print(f"R{idx+1}: Type={r['col_0']} | AnsA={r['col_4']} | AnsB={r['col_6']}")
        print(f"     Crit={r['col_1'][:60] if r['col_1'] else None}...")
        print(f"     ReasA={r['col_5'][:60] if r['col_5'] else None}...")
        print(f"     ReasB={r['col_7'][:60] if r['col_7'] else None}...")

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(inspect_page1())
