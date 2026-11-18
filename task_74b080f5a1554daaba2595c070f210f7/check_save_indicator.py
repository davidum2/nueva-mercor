import asyncio
from playwright.async_api import async_playwright

async def check_save_indicator():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    ctx = browser.contexts[0]
    rubric_page = None
    for pg in ctx.pages:
        if '/rubric/' in pg.url:
            rubric_page = pg
            break

    info = await rubric_page.evaluate("""() => {
        const text = document.body.innerText;
        const lines = text.split('\\n').map(l => l.trim()).filter(Boolean);
        const savedLines = lines.filter(l => l.toLowerCase().includes('save') || l.toLowerCase().includes('change'));
        return { savedLines };
    }""")
    print("Saved lines:", info['savedLines'])

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(check_save_indicator())
