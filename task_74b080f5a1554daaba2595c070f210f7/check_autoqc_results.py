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

    # Inspect AutoQC panel
    info = await mercor_page.evaluate("""() => {
        const text = document.body.innerText;
        const lines = text.split('\\n').map(l => l.trim()).filter(Boolean);
        
        const autoqcIndex = lines.findIndex(l => l === 'DELIVERABLE AUTOQC');
        if (autoqcIndex === -1) return { found: false };

        const autoqcSection = lines.slice(autoqcIndex, autoqcIndex + 60);

        // Also check if any buttons or tabs show pass/fail numbers
        const badges = Array.from(document.querySelectorAll('*')).filter(el => {
            const t = (el.innerText || '').trim();
            return t.includes('/17') || t.includes('Passed') || t.includes('Major issues') || t.includes('failing');
        }).map(el => el.innerText.trim()).slice(0, 15);

        return {
            found: true,
            section: autoqcSection,
            badges
        };
    }""")
    print("--- AutoQC Section ---")
    for l in info.get('section', []):
        print(" ", l)
    print("--- Badges ---")
    for b in info.get('badges', []):
        print(" ", b)

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
