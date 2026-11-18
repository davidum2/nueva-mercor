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

    if not mercor_page:
        print("No page found")
        await browser.close()
        await p.stop()
        return

    # Find and click Rubrics tab
    res = await mercor_page.evaluate("""() => {
        const btns = Array.from(document.querySelectorAll('button, a, [role="button"], div')).filter(el => {
            const t = (el.innerText || '').trim();
            return (t === 'Rubric' || t === 'Rubrics' || t === 'Rubric (create)' || t.includes('Rubric (create)')) && el.className.includes('truncate');
        });
        
        if (btns.length > 0) {
            btns[0].click();
            return { success: true, text: btns[0].innerText };
        }
        
        // Try any element with exact text Rubric in left sidebar
        const all = Array.from(document.querySelectorAll('*')).filter(el => {
            return (el.innerText || '').trim() === 'Rubric (create)' || (el.innerText || '').trim() === 'Rubric';
        });
        
        for (const el of all) {
            if (el.children.length === 0) {
                el.click();
                return { success: true, text: el.innerText, tag: el.tagName };
            }
        }
        
        return { success: false };
    }""")
    print("Click result:", res)
    await asyncio.sleep(2)

    status = await mercor_page.evaluate("""() => {
        const txt = document.body.innerText;
        return {
            hasTaskRubric: txt.includes('Task Rubric'),
            hasSpreadsheet: txt.includes('Spreadsheet'),
            length: txt.length
        };
    }""")
    print("Status after click:", status)

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
