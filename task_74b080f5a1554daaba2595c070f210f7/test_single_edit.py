import asyncio
from playwright.async_api import async_playwright

async def edit_single_cell(cell_sel, new_value):
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    ctx = browser.contexts[0]
    rubric_page = None
    for pg in ctx.pages:
        if '/rubric/' in pg.url:
            rubric_page = pg
            break

    # Phase 1: Enter edit mode
    res1 = await rubric_page.evaluate("""(sel) => {
        const cell = document.querySelector(sel);
        if (!cell) return { error: 'cell not found: ' + sel };
        cell.scrollIntoView({ block: 'center' });

        const key = Object.keys(cell).find(k => k.startsWith('__reactFiber$'));
        let f = cell[key];
        if (f && f.memoizedProps.onDoubleClick) {
            f.memoizedProps.onDoubleClick({ preventDefault: () => {}, stopPropagation: () => {} });
            return { dblclicked: true };
        }
        return { error: 'no onDoubleClick' };
    }""", cell_sel)
    print("Phase 1:", res1)
    await asyncio.sleep(0.5)

    # Phase 2: Set text
    res2 = await rubric_page.evaluate("""({ sel, val }) => {
        const cell = document.querySelector(sel);
        const ta = cell ? cell.querySelector('textarea') : document.querySelector('textarea');
        if (!ta) return { error: 'no textarea mounted' };

        const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
        setter.call(ta, val);
        ta.dispatchEvent(new Event('input', { bubbles: true }));
        ta.dispatchEvent(new Event('change', { bubbles: true }));
        ta.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', bubbles: true }));
        ta.blur();

        return { success: true };
    }""", { 'sel': cell_sel, 'val': new_value })
    print("Phase 2:", res2)
    await asyncio.sleep(0.5)

    # Phase 3: Check value
    actual = await rubric_page.evaluate("""(sel) => {
        return document.querySelector(sel)?.innerText?.trim();
    }""", cell_sel)
    print("Phase 3 actual text:", actual)

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    val = "Yes. Model A's patch in artifact_files_a/0.patch retains case MISSING_PATH and adds case INVALID_PATH. In both CompactSpawnLogContext and ExpandedSpawnLogContext, its output loop uses setMissingPath for absent outputs and setInvalidPath for wrong-type outputs, recording them in a distinct category."
    asyncio.run(edit_single_cell('[data-cell="1-5"]', val))
