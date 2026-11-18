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

    # Click Save Changes if enabled
    save_info = await mercor_page.evaluate("""() => {
        const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.trim() === 'Save Changes');
        if (btn) {
            const wasDisabled = btn.disabled;
            btn.click();
            return { found: true, wasDisabled };
        }
        return { found: false };
    }""")
    print("Save button info:", save_info)
    await asyncio.sleep(2.0)

    # Trigger AutoQC rerun
    rerun_info = await mercor_page.evaluate("""() => {
        const btns = Array.from(document.querySelectorAll('button'));
        // Try "Rerun 3 failing" or "Run AutoQC"
        const target = btns.find(b => b.innerText.includes('Rerun 3 failing') || b.innerText.includes('Run AutoQC'));
        if (target) {
            target.click();
            return { clicked: true, text: target.innerText };
        }
        return { clicked: false, availableButtons: btns.map(b => b.innerText.trim()).filter(t => t.includes('AutoQC') || t.includes('Rerun')) };
    }""")
    print("Rerun info:", rerun_info)

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
