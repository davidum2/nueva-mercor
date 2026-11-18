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

    # 1. Update Cell 7-1 (Rubric 8 criteria)
    r8_criteria = "Does the change avoid adding unrequested fields to proto messages other than File and Output (such as leaving ExecLogEntry.File without symlink fields)?"
    r8_res = await mercor_page.evaluate("""(val) => {
        const cell = document.querySelector('[data-cell="7-1"]');
        if (!cell) return { error: 'no cell 7-1' };

        const key = Object.keys(cell).find(k => k.startsWith('__reactFiber$'));
        let f = cell[key];
        
        // Enter edit mode
        if (f.memoizedProps.onDoubleClick) {
            f.memoizedProps.onDoubleClick({
                preventDefault: () => {},
                stopPropagation: () => {}
            });
        }
        
        const ta = cell.querySelector('textarea');
        if (!ta) return { error: 'no textarea mounted' };

        const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
        setter.call(ta, val);
        ta.dispatchEvent(new Event('input', { bubbles: true }));
        ta.dispatchEvent(new Event('change', { bubbles: true }));

        ta.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', bubbles: true }));
        ta.blur();

        return { success: true };
    }""", r8_criteria)
    print("Rubric 8 criteria update:", r8_res)
    await asyncio.sleep(0.5)

    # 2. Update Textareas for Rubric 2 Reason B and Rubric 6 Reason B
    tas_res = await mercor_page.evaluate("""() => {
        const tas = Array.from(document.querySelectorAll('textarea'));
        const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
        const updates = [];

        for (let i = 0; i < tas.length; i++) {
            const ta = tas[i];
            const val = ta.value;

            // Rubric 2 Reason B
            if (val.includes('ExceLogEntry.Output') || val.includes('CompactSpawnLogContestTest.java')) {
                const fixed = val
                    .replace('ExceLogEntry.Output', 'ExecLogEntry.Output')
                    .replace('CompactSpawnLogContestTest.java', 'CompactSpawnLogContextTest.java')
                    .replace('unhanded', 'unhandled')
                    .replace('update test suite', 'updated test suite');
                setter.call(ta, fixed);
                ta.dispatchEvent(new Event('input', { bubbles: true }));
                ta.dispatchEvent(new Event('change', { bubbles: true }));
                updates.push({ idx: i, type: 'rubric_2_reason_b', fixedPreview: fixed.slice(0, 100) });
            }

            // Rubric 6 Reason B
            if (val.includes('SpawnLogContextTestBae.java') || val.includes('compiled executed, and passed')) {
                const fixed = val
                    .replace('SpawnLogContextTestBae.java', 'SpawnLogContextTestBase.java')
                    .replace('compiled executed, and passed', 'compiled, executed, and passed');
                setter.call(ta, fixed);
                ta.dispatchEvent(new Event('input', { bubbles: true }));
                ta.dispatchEvent(new Event('change', { bubbles: true }));
                updates.push({ idx: i, type: 'rubric_6_reason_b', fixedPreview: fixed.slice(0, 100) });
            }
        }
        return updates;
    }""")
    print("Textarea updates:", tas_res)
    await asyncio.sleep(0.5)

    # 3. Click Save Changes
    save_res = await mercor_page.evaluate("""() => {
        const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.trim() === 'Save Changes');
        if (btn) {
            btn.click();
            return { clicked: true, disabled: btn.disabled };
        }
        return { clicked: false };
    }""")
    print("Save Changes:", save_res)
    await asyncio.sleep(2.0)

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
