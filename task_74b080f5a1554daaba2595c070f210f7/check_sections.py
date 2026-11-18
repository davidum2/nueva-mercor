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

    txt = await mercor_page.evaluate('document.body.innerText')
    lines = [l.strip() for l in txt.split('\n') if l.strip()]
    print(f"Total lines: {len(lines)}")
    print("First 20 lines:")
    for l in lines[:20]:
        print(" ", l)

    # Search for key sections
    for s in ['HOW THIS TASK WORKS', 'TASK BUNDLE', 'TRAJECTORY VIEWER', 'RUBRIC', 'RUBRIC COUNT', 'DELIVERABLE AUTOQC', 'REVIEWER FEEDBACK']:
        matching = [i for i, l in enumerate(lines) if s in l.upper()]
        print(f"Section '{s}': line indices {matching}")

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
