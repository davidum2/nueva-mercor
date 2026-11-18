import asyncio
from playwright.async_api import async_playwright

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def expand_autoqc():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]
    
    # Click the accordion DELIVERABLE AUTOQC
    header = page.locator('text="DELIVERABLE AUTOQC"')
    count = await header.count()
    print('Header count:', count)
    for i in range(count):
        el = header.nth(i)
        if await el.is_visible():
            await el.click()
            print('Clicked accordion header index', i)
            break
            
    await asyncio.sleep(2)
    await page.screenshot(path='autoqc_expanded.png')
    print('Saved autoqc_expanded.png')
    
    # Check text inside accordion
    text = await page.evaluate("""() => {
        const els = Array.from(document.querySelectorAll('*'));
        const autoqcHeader = els.find(el => el.innerText && el.innerText.trim() === 'DELIVERABLE AUTOQC');
        if (autoqcHeader && autoqcHeader.parentElement) {
            return autoqcHeader.parentElement.innerText;
        }
        return '';
    }""")
    print("AutoQC Accordion Text:\n", text[:500])
    await p.stop()

if __name__ == '__main__':
    asyncio.run(expand_autoqc())
