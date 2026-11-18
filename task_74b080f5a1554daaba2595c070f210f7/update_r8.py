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

    # 1. Scroll cell 7-1 into view and click
    status = await mercor_page.evaluate("""() => {
        const cell = document.querySelector('[data-cell="7-1"]');
        if (!cell) return { error: 'no cell 7-1' };
        cell.scrollIntoView({ block: 'center' });
        
        const key = Object.keys(cell).find(k => k.startsWith('__reactFiber$'));
        let f = cell[key];
        if (f.memoizedProps.onDoubleClick) {
            f.memoizedProps.onDoubleClick({
                preventDefault: () => {},
                stopPropagation: () => {}
            });
            return { dblclicked: true };
        }
        return { dblclicked: false };
    }""")
    print("Dblclick status:", status)
    await asyncio.sleep(0.5)

    # 2. Check and set textarea
    val = "Does the change avoid adding unrequested fields to proto messages other than File and Output (such as leaving ExecLogEntry.File without symlink fields)?"
    set_res = await mercor_page.evaluate("""(val) => {
        const cell = document.querySelector('[data-cell="7-1"]');
        const ta = cell ? cell.querySelector('textarea') : document.querySelector('textarea');
        if (!ta) return { error: 'no textarea' };

        const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
        setter.call(ta, val);
        ta.dispatchEvent(new Event('input', { bubbles: true }));
        ta.dispatchEvent(new Event('change', { bubbles: true }));
        ta.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', bubbles: true }));
        ta.blur();

        return { success: true };
    }""", val)
    print("Set res:", set_res)
    await asyncio.sleep(0.5)

    # 3. Check cell text
    c_text = await mercor_page.evaluate("""() => {
        const cell = document.querySelector('[data-cell="7-1"]');
        return cell ? cell.innerText.trim() : null;
    }""")
    print("Cell 7-1 text now:", c_text)

    # Click Save Changes
    await mercor_page.evaluate("""() => {
        const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.trim() === 'Save Changes');
        if (btn) btn.click();
    }""")

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
