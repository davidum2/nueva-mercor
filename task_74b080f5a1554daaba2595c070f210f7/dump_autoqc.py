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

    if not mercor_page:
        print("No page found")
        await browser.close()
        await p.stop()
        return

    # Check AutoQC findings
    script = """() => {
        const text = document.body.innerText;
        // Also look for react components / autoqc cards
        return text;
    }"""
    
    data = await mercor_page.evaluate(script)
    with open('autoqc_full_text.txt', 'w', encoding='utf-8') as f:
        f.write(data)
    
    # Also inspect React Fiber for AutoQC state
    fiber_script = """() => {
        // Look for autoqc results in window / react state
        const results = [];
        // traverse fiber or query selectors
        const items = document.querySelectorAll('[class*="accordion"], [class*="card"], [class*="issue"], div');
        for (const it of items) {
            if (it.innerText && (it.innerText.includes('Each Rubric Maps') || it.innerText.includes('Pass Rate') || it.innerText.includes('Required Annotation Fields'))) {
                results.push(it.innerText.trim());
            }
        }
        return results;
    }"""
    details = await mercor_page.evaluate(fiber_script)
    with open('autoqc_details.json', 'w', encoding='utf-8') as f:
        json.dump(details, f, indent=2)

    print("Successfully extracted AutoQC details!")
    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
