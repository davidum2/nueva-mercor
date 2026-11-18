import asyncio
from playwright.async_api import async_playwright

async def inspect_page0_a():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page0 = browser.contexts[0].pages[0]

    # Click on "1 · Agent solution A" tab
    await page0.evaluate("""() => {
        const tabs = Array.from(document.querySelectorAll('*')).filter(el => {
            return (el.innerText || '').trim() === '1 · Agent solution A' && el.children.length === 0;
        });
        if (tabs.length > 0) {
            tabs[0].click();
        }
    }""")
    await asyncio.sleep(1.0)

    # Now inspect comboboxes and textareas
    info = await page0.evaluate("""() => {
        const cbs = Array.from(document.querySelectorAll('[role="combobox"]')).map((el, i) => {
            const parent = el.closest('div')?.parentElement?.parentElement?.innerText || '';
            const label = parent.split('\\n')[0];
            return { i, text: el.innerText.trim(), label: label.slice(0, 50) };
        });
        const tas = Array.from(document.querySelectorAll('textarea')).map((el, i) => {
            const parent = el.closest('div')?.parentElement?.parentElement?.innerText || '';
            const label = parent.split('\\n')[0];
            return { i, val: el.value.slice(0, 80), label: label.slice(0, 50) };
        });
        return { cbs, tas };
    }""")
    print("Page 0 Comboboxes under Model A:")
    for c in info['cbs']:
        if 'Rubric' in c['label'] or 'answer' in c['label']:
            print(" ", c)

    print("\nPage 0 Textareas under Model A:")
    for t in info['tas']:
        if 'Rubric' in t['label'] or 'reason' in t['label']:
            print(" ", t)

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(inspect_page0_a())
