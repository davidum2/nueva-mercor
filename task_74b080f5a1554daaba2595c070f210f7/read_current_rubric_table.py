import asyncio
import json
from playwright.async_api import async_playwright

async def run():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    mercor_page = None
    for ctx in browser.contexts:
        for page in ctx.pages:
            if 'mercor.com' in page.url:
                mercor_page = page
                break
        if mercor_page:
            break

    # Expand accordion if needed
    await mercor_page.evaluate("""() => {
        const table = document.querySelector('[data-cell="1-1"]');
        if (table) return;
        const els = Array.from(document.querySelectorAll('*')).filter(el => (el.innerText || '').trim() === 'RUBRIC' && el.children.length === 0);
        if (els.length > 0) els[0].parentElement.click();
    }""")
    await asyncio.sleep(1.0)

    rows = await mercor_page.evaluate("""() => {
        const result = [];
        for (let r = 0; r < 15; r++) {
            const rowData = {};
            for (let c = 0; c < 5; c++) {
                const cell = document.querySelector(`[data-cell="${r}-${c}"]`);
                rowData[`col_${c}`] = cell ? cell.innerText.trim() : null;
            }
            result.push(rowData);
        }
        return result;
    }""")
    print("Rubric spreadsheet rows:")
    for i, r in enumerate(rows):
        print(f"Row {i+1}: criteria='{r['col_1']}' | dim='{r['col_2']}' | source='{r['col_3']}'")

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
