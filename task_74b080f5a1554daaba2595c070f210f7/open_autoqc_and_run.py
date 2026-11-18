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

    # Look for element with text DELIVERABLE AUTOQC
    res = await task_page.evaluate("""() => {
        const els = Array.from(document.querySelectorAll('*')).filter(el => {
            return (el.innerText || '').trim() === 'DELIVERABLE AUTOQC' && el.children.length === 0;
        });
        if (els.length > 0) {
            const header = els[0].closest('button') || els[0].parentElement;
            header.scrollIntoView({ block: 'center' });
            header.click();
            return { clicked: true, tag: header.tagName };
        }
        return { clicked: false };
    }""")
    print("Click header:", res)
    await asyncio.sleep(1.0)

    # Now search for "Run AutoQC"
    run_btn = await task_page.evaluate("""() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const b = btns.find(b => (b.innerText || '').trim() === 'Run AutoQC' || b.innerText.includes('Rerun'));
        if (b) {
            b.scrollIntoView({ block: 'center' });
            b.click();
            return { clicked: true, text: b.innerText };
        }
        return { clicked: false, all: btns.map(x => x.innerText.trim()).filter(t => t.includes('AutoQC')) };
    }""")
    print("Run AutoQC:", run_btn)

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
