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

    new_val = "Does the test reconstruction in CompactSpawnLogContextTest handle all output categories when an action output has a filesystem type mismatch?"

    edit_res = await mercor_page.evaluate("""(val) => {
        const cell = document.querySelector('[data-cell="1-1"]');
        if (!cell) return { error: 'no cell' };

        const key = Object.keys(cell).find(k => k.startsWith('__reactFiber$'));
        let f = cell[key];
        
        // 1. Enter edit mode
        if (f.memoizedProps.onDoubleClick) {
            f.memoizedProps.onDoubleClick({
                preventDefault: () => {},
                stopPropagation: () => {}
            });
        }
        
        // Find textarea
        const ta = cell.querySelector('textarea');
        if (!ta) return { error: 'no textarea mounted' };

        // 2. Set value
        const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
        setter.call(ta, val);
        ta.dispatchEvent(new Event('input', { bubbles: true }));
        ta.dispatchEvent(new Event('change', { bubbles: true }));

        // 3. Commit edit by blurring / Enter
        ta.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', bubbles: true }));
        ta.blur();

        return { success: true };
    }""", new_val)
    print("Edit res:", edit_res)
    await asyncio.sleep(0.5)

    # Check cell text
    cell_text = await mercor_page.evaluate("""() => {
        const cell = document.querySelector('[data-cell="1-1"]');
        return cell ? cell.innerText.trim() : null;
    }""")
    print("Cell 1-1 text now:", cell_text)

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
