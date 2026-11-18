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

    status = await mercor_page.evaluate("""() => {
        const cell = document.querySelector('[data-cell="1-1"]');
        if (!cell) {
            // Check if accordion is closed
            const els = Array.from(document.querySelectorAll('*')).filter(el => (el.innerText || '').trim() === 'RUBRIC' && el.children.length === 0);
            if (els.length > 0) {
                els[0].parentElement.click();
                return { action: 'clicked_accordion' };
            }
            return { action: 'rubric_header_not_found' };
        }
        
        // If cell exists, simulate focus and click
        cell.scrollIntoView({ block: 'center' });
        cell.focus();
        cell.dispatchEvent(new MouseEvent('mousedown', { bubbles: true }));
        cell.dispatchEvent(new MouseEvent('mouseup', { bubbles: true }));
        cell.dispatchEvent(new MouseEvent('click', { bubbles: true }));

        return {
            action: 'clicked_cell',
            cellText: cell.innerText
        };
    }""")
    print("Status:", status)

    if status.get('action') == 'clicked_accordion':
        await asyncio.sleep(1.0)

    # Now press Enter via mercor_page.keyboard
    await mercor_page.keyboard.press('Enter')
    await asyncio.sleep(0.5)

    active_info = await mercor_page.evaluate("""() => {
        const active = document.activeElement;
        const cell = document.querySelector('[data-cell="1-1"]');
        const ta = cell ? cell.querySelector('textarea') : document.querySelector('textarea');
        return {
            activeTag: active ? active.tagName : null,
            activeClass: active ? active.className : null,
            activeVal: active ? active.value : null,
            hasTextareaInCell: !!cell?.querySelector('textarea'),
            hasAnyTextareaVisible: !!ta
        };
    }""")
    print("Active info after Enter:", active_info)

    # Press Escape to close edit mode
    await mercor_page.keyboard.press('Escape')

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
