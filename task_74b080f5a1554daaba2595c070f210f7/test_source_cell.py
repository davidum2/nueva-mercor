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

    info = await mercor_page.evaluate("""() => {
        const cell = document.querySelector('[data-cell="14-3"]');
        if (!cell) return 'no cell 14-3';

        const key = Object.keys(cell).find(k => k.startsWith('__reactFiber$'));
        let f = cell[key];
        
        return {
            text: cell.innerText,
            onDoubleClick: !!f.memoizedProps.onDoubleClick,
            children: f.memoizedProps.children ? 'has children' : 'no children'
        };
    }""")
    print("Cell 14-3 info:", info)

    # Call onDoubleClick to see what mounts
    open_res = await mercor_page.evaluate("""() => {
        const cell = document.querySelector('[data-cell="14-3"]');
        const key = Object.keys(cell).find(k => k.startsWith('__reactFiber$'));
        let f = cell[key];
        if (f.memoizedProps.onDoubleClick) {
            f.memoizedProps.onDoubleClick({
                preventDefault: () => {},
                stopPropagation: () => {}
            });
        }
        return 'called dblclick';
    }""")
    print("Open res:", open_res)
    await asyncio.sleep(0.5)

    popover_info = await mercor_page.evaluate("""() => {
        const cell = document.querySelector('[data-cell="14-3"]');
        const popovers = Array.from(document.querySelectorAll('[role="dialog"], [role="listbox"], [role="menu"], [data-radix-popper-content-wrapper]'));
        const options = Array.from(document.querySelectorAll('[role="option"], button'));
        return {
            cellHTML: cell.innerHTML,
            popoversCount: popovers.length,
            popoverHTML: popovers[0] ? popovers[0].outerHTML.slice(0, 300) : null,
            options: options.map(o => (o.innerText || '').trim()).filter(t => t.includes('COMMON') || t.includes('PROMPT') || t.includes('INFERRABLE'))
        };
    }""")
    print("Popover info:", json.dumps(popover_info, indent=2))

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
