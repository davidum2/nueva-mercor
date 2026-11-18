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

    data = await mercor_page.evaluate("""() => {
        // Find "Before you submit"
        const all = Array.from(document.querySelectorAll('*'));
        const el = all.find(e => (e.innerText || '').trim() === 'Before you submit');
        if (!el) return { found: false };
        
        // Find container
        let parent = el.parentElement;
        while (parent && !parent.innerText.includes('Submit for Final QC') && parent !== document.body) {
            parent = parent.parentElement;
        }
        
        const items = Array.from((parent || document.body).querySelectorAll('*'))
            .filter(e => e.children.length === 0 && (e.innerText || '').trim().length > 0)
            .map(e => ({
                text: e.innerText.trim(),
                color: window.getComputedStyle(e).color
            }));
            
        return { found: true, items: items.slice(0, 100) };
    }""")
    print("Found:", data.get('found'))
    for it in data.get('items', [])[:60]:
        print(f"  [{it['color']}] {it['text']}")

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
