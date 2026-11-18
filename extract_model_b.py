import asyncio
import os
import json
from playwright.async_api import async_playwright

async def main():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [p for ctx in browser.contexts for p in ctx.pages if 'mercor.com' in p.url][0]

    # Find the Model B tab button inside the Trajectory Viewer
    model_b_clicked = await page.evaluate('''() => {
        const btns = Array.from(document.querySelectorAll('button, [role="tab"]'));
        // Find specifically within Trajectory viewer
        const mb = btns.find(b => b.innerText.trim() === 'Model B');
        if (mb) {
            mb.click();
            return true;
        }
        return false;
    }''')
    print("Clicked Model B:", model_b_clicked)
    await asyncio.sleep(2.0)

    # Click Show more
    await page.evaluate('''() => {
        const showMores = Array.from(document.querySelectorAll('button')).filter(b => b.innerText.includes('Show more'));
        showMores.forEach(b => b.click());
    }''')
    await asyncio.sleep(1.0)

    # Get the text of Trajectory Viewer
    tv_text = await page.evaluate('''() => {
        const headers = Array.from(document.querySelectorAll('h1, h2, h3, h4, div')).filter(d => d.innerText && d.innerText.includes('TRAJECTORY VIEWER'));
        if (headers.length > 0) {
            let container = headers[0].parentElement;
            while (container && container.innerText.length < 500) {
                container = container.parentElement;
            }
            return container ? container.innerText : document.body.innerText;
        }
        return document.body.innerText;
    }''')

    with open('task_74b080f5a1554daaba2595c070f210f7/model_b/trajectory_viewer_b.txt', 'w', encoding='utf-8') as f:
        f.write(tv_text)
    print("Guardado model_b/trajectory_viewer_b.txt")

if __name__ == "__main__":
    asyncio.run(main())
