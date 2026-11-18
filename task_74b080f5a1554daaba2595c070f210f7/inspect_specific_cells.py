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

    cells_data = await mercor_page.evaluate("""() => {
        const res = {};
        for (const row of [1, 7, 14]) {
            res[row] = {};
            for (let col = 0; col < 5; col++) {
                const cell = document.querySelector(`[data-cell="${row}-${col}"]`);
                if (cell) {
                    res[row][col] = {
                        text: cell.innerText.trim(),
                        hasInput: !!cell.querySelector('input, select, textarea'),
                        innerHTML: cell.innerHTML
                    };
                }
            }
        }
        return res;
    }""")
    print("Cells data:", json.dumps(cells_data, indent=2))

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
