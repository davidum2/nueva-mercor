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

    if not rubric_page:
        print("No rubric page found")
        await browser.close()
        await p.stop()
        return

    print("Found rubric page:", rubric_page.url)

    # Inspect columns, table, and data on rubric page
    info = await rubric_page.evaluate("""() => {
        const text = document.body.innerText;
        const lines = text.split('\\n').map(l => l.trim()).filter(Boolean);
        
        // Find headers
        const headers = Array.from(document.querySelectorAll('th, [role="columnheader"]')).map(h => h.innerText.trim());
        
        // Find cells
        const sampleCells = [];
        for (let r = 0; r < 5; r++) {
            const row = [];
            for (let c = 0; c < 10; c++) {
                const cell = document.querySelector(`[data-cell="${r}-${c}"]`);
                if (cell) row.push(cell.innerText.trim().slice(0, 30));
            }
            if (row.length > 0) sampleCells.push(row);
        }

        return {
            title: document.title,
            headers,
            sampleCells,
            lineSample: lines.slice(0, 35)
        };
    }""")

    print(json.dumps(info, indent=2))

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
