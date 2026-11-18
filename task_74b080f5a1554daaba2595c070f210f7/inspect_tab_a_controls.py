import asyncio
import json
from playwright.async_api import async_playwright

async def inspect_page0_tabs():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = browser.contexts[0].pages[0]

    # Click tab "1 · Agent solution A"
    await page.evaluate("""() => {
        const tabs = Array.from(document.querySelectorAll('*')).filter(el => {
            return (el.innerText || '').trim() === '1 · Agent solution A' && el.children.length === 0;
        });
        if (tabs.length > 0) {
            tabs[0].click();
        }
    }""")
    await asyncio.sleep(1.0)

    # Dump all textareas and comboboxes
    info = await page.evaluate("""() => {
        const cbs = Array.from(document.querySelectorAll('[role="combobox"]')).map((el, i) => {
            const parent = el.closest('div')?.parentElement?.parentElement?.innerText || '';
            const label = parent.split('\\n')[0];
            return { i, text: el.innerText.trim(), label: label.slice(0, 50) };
        });
        const tas = Array.from(document.querySelectorAll('textarea')).map((el, i) => {
            const parent = el.closest('div')?.parentElement?.parentElement?.innerText || '';
            const label = parent.split('\\n')[0];
            return { i, valPreview: el.value.slice(0, 100), label: label.slice(0, 50) };
        });
        return { cbs, tas };
    }""")

    print(f"Total comboboxes under tab A: {len(info['cbs'])}")
    for c in info['cbs']:
        print(f"  CB [{c['i']}] {c['label']} -> {c['text']}")

    print(f"\nTotal textareas under tab A: {len(info['tas'])}")
    for t in info['tas']:
        print(f"  TA [{t['i']}] {t['label']} -> {t['valPreview']}")

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(inspect_page0_tabs())
