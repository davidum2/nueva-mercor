import asyncio
from playwright.async_api import async_playwright

async def test_r10_ans():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    ctx = browser.contexts[0]
    rubric_page = None
    for pg in ctx.pages:
        if '/rubric/' in pg.url:
            rubric_page = pg
            break

    # 1. Double click cell 9-4
    open_res = await rubric_page.evaluate("""() => {
        const cell = document.querySelector('[data-cell="9-4"]');
        if (!cell) return { error: 'no cell 9-4' };
        cell.scrollIntoView({ block: 'center' });
        const key = Object.keys(cell).find(k => k.startsWith('__reactFiber$'));
        let f = cell[key];
        if (f && f.memoizedProps.onDoubleClick) {
            f.memoizedProps.onDoubleClick({ preventDefault: () => {}, stopPropagation: () => {} });
        }
        return { success: true };
    }""")
    print("Open res:", open_res)
    await asyncio.sleep(0.5)

    # 2. Check options visible
    opts = await rubric_page.evaluate("""() => {
        const options = Array.from(document.querySelectorAll('[role="option"], [role="menuitem"], div, span')).filter(el => {
            const t = (el.innerText || '').trim();
            return (t === 'YES' || t === 'NO') && el.children.length === 0;
        }).map(el => ({ tag: el.tagName, role: el.getAttribute('role'), text: el.innerText.trim() }));
        return options;
    }""")
    print("Found options:", opts)

    # 3. Select YES
    sel_res = await rubric_page.evaluate("""() => {
        const options = Array.from(document.querySelectorAll('[role="option"], div, span')).filter(el => {
            const t = (el.innerText || '').trim();
            return t === 'YES' && el.children.length === 0;
        });
        if (options.length > 0) {
            const target = options[options.length - 1]; // usually latest overlay
            target.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true }));
            target.dispatchEvent(new MouseEvent('mousedown', { bubbles: true }));
            target.dispatchEvent(new PointerEvent('pointerup', { bubbles: true }));
            target.dispatchEvent(new MouseEvent('mouseup', { bubbles: true }));
            target.dispatchEvent(new MouseEvent('click', { bubbles: true }));
            return { clicked: true, text: target.innerText };
        }
        return { clicked: false };
    }""")
    print("Sel res:", sel_res)
    await asyncio.sleep(1.0)

    # 4. Check cell 9-4 value
    val = await rubric_page.evaluate("""() => {
        return document.querySelector('[data-cell="9-4"]')?.innerText?.trim();
    }""")
    print("Cell 9-4 value now:", val)

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(test_r10_ans())
