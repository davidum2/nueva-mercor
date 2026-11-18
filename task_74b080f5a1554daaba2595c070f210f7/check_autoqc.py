import asyncio
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
        print("No mercor page found")
        await browser.close()
        await p.stop()
        return

    # Check tab buttons on page
    tabs = await mercor_page.evaluate("""() => {
        const buttons = Array.from(document.querySelectorAll('button, [role="tab"], div[class*="tab"]'));
        return buttons.map(b => ({
            text: b.innerText ? b.innerText.trim() : '',
            role: b.getAttribute('role'),
            className: b.className
        })).filter(b => b.text && b.text.length < 50 && (b.text.includes('AutoQC') || b.text.includes('G') || b.text.includes('Review') || b.text.includes('Feedback')));
    }""")
    print("Tabs found:", tabs)

    # Check if there is any AutoQC element or status on page
    autoqc_info = await mercor_page.evaluate("""() => {
        const allText = document.body.innerText;
        const matches = [];
        const lines = allText.split('\\n');
        for (let i = 0; i < lines.length; i++) {
            if (lines[i].includes('AutoQC') || lines[i].includes('autoqc') || lines[i].includes('Deliverable AutoQC')) {
                matches.push({ line: i, text: lines[i], context: lines.slice(Math.max(0, i-2), Math.min(lines.length, i+15)).join('\\n') });
            }
        }
        return matches;
    }""")
    print(f"AutoQC matches in DOM: {len(autoqc_info)}")
    for m in autoqc_info[:5]:
        print("--- Match ---")
        print(m['context'])

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
