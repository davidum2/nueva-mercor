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

    info = await mercor_page.evaluate("""() => {
        const text = document.body.innerText;
        const isRunning = text.includes('AutoQC is running');
        const lines = text.split('\\n').map(l => l.trim()).filter(Boolean);
        const autoqcIdx = lines.findIndex(l => l === 'DELIVERABLE AUTOQC');
        const snippet = autoqcIdx !== -1 ? lines.slice(autoqcIdx, autoqcIdx + 40) : [];
        return { isRunning, snippet };
    }""")
    print("AutoQC Running:", info['isRunning'])
    print("AutoQC snippet:")
    for s in info['snippet']:
        print(" ", s.encode('ascii', errors='replace').decode('ascii'))

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
