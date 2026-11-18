import asyncio
from playwright.async_api import async_playwright

async def check_submit_status():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = browser.contexts[0].pages[0]

    info = await page.evaluate("""() => {
        const text = document.body.innerText;
        const lines = text.split('\\n').map(l => l.trim()).filter(Boolean);
        const navIdx = lines.findIndex(l => l === 'Before you submit');
        const snippet = navIdx !== -1 ? lines.slice(navIdx, navIdx + 25) : [];

        const submitBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('Submit for Final QC'));
        return {
            snippet,
            submitBtnExists: !!submitBtn,
            submitBtnDisabled: submitBtn ? submitBtn.disabled : null,
            submitBtnText: submitBtn ? submitBtn.innerText.trim() : null
        };
    }""")
    print("Submit status info:")
    for s in info['snippet']:
        print(" ", s)
    print("Submit button:", info['submitBtnText'], "| Disabled:", info['submitBtnDisabled'])

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(check_submit_status())
