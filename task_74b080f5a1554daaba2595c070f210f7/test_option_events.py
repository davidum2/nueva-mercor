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

    # Open dropdown again
    await mercor_page.evaluate("""() => {
        const cell = document.querySelector('[data-cell="14-3"]');
        const key = Object.keys(cell).find(k => k.startsWith('__reactFiber$'));
        let f = cell[key];
        if (f.memoizedProps.onDoubleClick) {
            f.memoizedProps.onDoubleClick({
                preventDefault: () => {},
                stopPropagation: () => {}
            });
        }
    }""")
    await asyncio.sleep(0.5)

    res = await mercor_page.evaluate("""() => {
        const options = Array.from(document.querySelectorAll('[role="option"]'));
        const target = options.find(o => o.innerText.includes('COMMON_ENGINEERING_KNOWLEDGE'));
        if (!target) return { found: false, all: options.map(o => o.innerText) };

        // Inspect target's fiber
        const key = Object.keys(target).find(k => k.startsWith('__reactFiber$'));
        let f = target[key];
        const props = Object.keys(f?.memoizedProps || {});

        // Try pointerdown + pointerup + click
        target.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true }));
        target.dispatchEvent(new MouseEvent('mousedown', { bubbles: true }));
        target.dispatchEvent(new PointerEvent('pointerup', { bubbles: true }));
        target.dispatchEvent(new MouseEvent('mouseup', { bubbles: true }));
        target.dispatchEvent(new MouseEvent('click', { bubbles: true }));

        return {
            found: true,
            props,
            targetHTML: target.outerHTML
        };
    }""")
    print("Option click res:", json.dumps(res, indent=2))
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
