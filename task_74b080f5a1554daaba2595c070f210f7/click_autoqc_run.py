import asyncio
from playwright.async_api import async_playwright

async def run():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    ctx = browser.contexts[0]
    task_page = None
    for pg in ctx.pages:
        if 'task_74b080f5a1554daaba2595c070f210f7/?' in pg.url:
            task_page = pg
            break

    # Click Deliverable AutoQC in navigation/sidebar
    res = await task_page.evaluate("""() => {
        const btns = Array.from(document.querySelectorAll('button, [role="tab"], div'));
        const nav = btns.find(b => (b.innerText || '').trim() === 'Deliverable AutoQC');
        if (nav) {
            nav.click();
            return { clickedNav: true };
        }
        return { clickedNav: false };
    }""")
    print("Nav result:", res)
    await asyncio.sleep(1.0)

    # Now find and click 'Run AutoQC'
    run_btn = await task_page.evaluate("""() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const target = btns.find(b => (b.innerText || '').trim() === 'Run AutoQC' || b.innerText.includes('Rerun'));
        if (target) {
            target.click();
            return { clicked: true, text: target.innerText.trim() };
        }
        return { clicked: false, available: btns.map(b => b.innerText.trim()).filter(t => t.includes('AutoQC') || t.includes('Run') || t.includes('Rerun')) };
    }""")
    print("Run button:", run_btn)

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
