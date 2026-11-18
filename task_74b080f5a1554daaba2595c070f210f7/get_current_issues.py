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

    failing_info = await mercor_page.evaluate("""() => {
        const text = document.body.innerText;
        const lines = text.split('\\n').map(l => l.trim()).filter(Boolean);
        
        // Find Major issues and Minor issues headers
        const majorIdx = lines.findIndex(l => l.includes('Major issues'));
        const passedIdx = lines.findIndex(l => l === 'Passed' || l.startsWith('Passed ('));
        
        return {
            issuesSlice: (majorIdx !== -1 && passedIdx !== -1) ? lines.slice(majorIdx, passedIdx) : lines.slice(0, 100)
        };
    }""")
    
    print("--- ALL CURRENT ISSUES ---")
    for l in failing_info['issuesSlice']:
        print(" ", l.encode('ascii', errors='replace').decode('ascii'))

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
