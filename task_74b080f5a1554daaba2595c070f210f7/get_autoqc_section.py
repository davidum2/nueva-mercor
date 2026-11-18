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

    cards = await mercor_page.evaluate("""() => {
        // Find elements with findings or issues
        const cards = Array.from(document.querySelectorAll('*')).filter(el => {
            const t = el.innerText || '';
            return (t.includes('MAJOR') || t.includes('MINOR')) && el.children.length > 0 && el.children.length < 10;
        });
        
        // Let's also look for text after 'Rerun'
        const allText = document.body.innerText;
        const autoqcStart = allText.indexOf('DELIVERABLE AUTOQC');
        const autoqcEnd = allText.indexOf('SUBMIT REVIEW');
        const section = autoqcStart !== -1 ? allText.slice(autoqcStart, autoqcEnd !== -1 ? autoqcEnd : autoqcStart + 3000) : '';
        
        return { section };
    }""")
    
    lines = [l.strip() for l in cards['section'].split('\n') if l.strip()]
    for l in lines:
        print(" ", l.encode('ascii', errors='replace').decode('ascii'))

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
