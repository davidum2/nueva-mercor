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

    # Look for any mention of answer (A) in the entire html source
    html = await mercor_page.content()
    has_r1_a = 'Rubric 1 · answer (A)' in html
    has_r2_a = 'Rubric 2 · answer (A)' in html
    print("Contains 'Rubric 1 · answer (A)' in HTML:", has_r1_a)
    print("Contains 'Rubric 2 · answer (A)' in HTML:", has_r2_a)

    # Let's inspect React state / form values to see if rubricAnswersA exists
    state_info = await mercor_page.evaluate("""() => {
        // Find form registrant
        const forms = Array.from(document.querySelectorAll('form'));
        // Or search window or fiber
        return {
            localStorage: Object.keys(localStorage),
        };
    }""")
    print("State info:", state_info)

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
