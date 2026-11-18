import asyncio
import os
import re
import json
from playwright.async_api import async_playwright

OUTPUT_DIR = os.path.join(os.getcwd(), "task_74b080f5a1554daaba2595c070f210f7", "model_a")

async def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [p for ctx in browser.contexts for p in ctx.pages if 'mercor.com' in p.url][0]

    # Ensure Trajectory Viewer is open
    await page.evaluate('''() => {
        const btns = Array.from(document.querySelectorAll('li button')).filter(b => b.innerText.trim() === 'Trajectory Viewer');
        if (btns.length > 0) btns[0].click();
    }''')
    await asyncio.sleep(1.5)

    # Ensure Model A is selected
    await page.evaluate('''() => {
        const btns = Array.from(document.querySelectorAll('button')).filter(b => b.innerText.trim() === 'Model A');
        if (btns.length > 0) btns[0].click();
    }''')
    await asyncio.sleep(1.0)

    # Ensure LOGS is selected
    await page.evaluate('''() => {
        const btns = Array.from(document.querySelectorAll('button')).filter(b => b.innerText.trim() === 'LOGS');
        if (btns.length > 0) btns[0].click();
    }''')
    await asyncio.sleep(1.0)

    # Click 'Expand all'
    print("Clicking Expand all...")
    await page.evaluate('''() => {
        const btns = Array.from(document.querySelectorAll('button')).filter(b => b.innerText.trim() === 'Expand all');
        if (btns.length > 0) btns[0].click();
    }''')
    await asyncio.sleep(2.0)

    # Expand any remaining 'Show more' or 'Show X more lines'
    print("Expanding nested 'Show more' and code blocks...")
    expanded_count = await page.evaluate('''() => {
        const showBtns = Array.from(document.querySelectorAll('button')).filter(b => {
            const txt = b.innerText.trim().toLowerCase();
            return txt.includes('show more') || txt.includes('more lines') || txt.includes('show all');
        });
        showBtns.forEach(b => {
            try { b.click(); } catch (e) {}
        });
        return showBtns.length;
    }''')
    print(f"Clicked {expanded_count} expandable items.")
    await asyncio.sleep(2.0)

    # Extract all text from the logs container
    logs_data = await page.evaluate('''() => {
        // Find the logs container
        const headers = Array.from(document.querySelectorAll('*')).filter(el => el.innerText && el.innerText.includes('Collapse all'));
        let container = null;
        if (headers.length > 0) {
            container = headers[0].closest('.overflow-y-auto, [role=\"tabpanel\"], div');
        }
        if (!container) {
            container = document.body;
        }

        // Extract individual step cards if possible
        const stepElements = Array.from(container.querySelectorAll('*')).filter(el => {
            return el.innerText && el.innerText.match(/^Step \\d+/);
        });

        return {
            fullText: container.innerText
        };
    }''')

    raw_text_path = os.path.join(OUTPUT_DIR, "logs_expanded_raw.txt")
    with open(raw_text_path, "w", encoding="utf-8") as f:
        f.write(logs_data["fullText"])
    print(f"Guardado logs_expanded_raw.txt ({len(logs_data['fullText'])} caracteres)")

if __name__ == "__main__":
    asyncio.run(main())
