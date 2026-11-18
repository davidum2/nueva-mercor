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

    select_res = await mercor_page.evaluate("""() => {
        // Look for option with COMMON_ENGINEERING_KNOWLEDGE
        const options = Array.from(document.querySelectorAll('[role="option"], div, span')).filter(el => {
            return (el.innerText || '').trim() === 'COMMON_ENGINEERING_KNOWLEDGE' && el.children.length === 0;
        });
        if (options.length > 0) {
            options[0].click();
            return { clicked: true, text: options[0].innerText };
        }
        return { clicked: false, count: options.length };
    }""")
    print("Select res:", select_res)
    await asyncio.sleep(0.5)

    cell_text = await mercor_page.evaluate("""() => {
        const cell = document.querySelector('[data-cell="14-3"]');
        return cell ? cell.innerText.trim() : null;
    }""")
    print("Cell 14-3 text now:", cell_text)

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
