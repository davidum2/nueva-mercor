import asyncio
from playwright.async_api import async_playwright

async def run():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    ctx = browser.contexts[0]
    
    task_page = None
    for pg in ctx.pages:
        if 'task_74b080f5a1554daaba2595c070f210f7/?' in pg.url:
            task_page = pg
            break

    if not task_page:
        print("Task page not found")
        await browser.close()
        await p.stop()
        return

    print("Task page found:", task_page.url)
    print("Reloading task page to fetch updated rubric table from database...")
    await task_page.reload()
    await asyncio.sleep(4.0)

    # Save Changes if button is enabled
    save_res = await task_page.evaluate("""() => {
        const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.trim() === 'Save Changes');
        if (btn && !btn.disabled) {
            btn.click();
            return { clicked: true };
        }
        return { clicked: false, disabled: btn ? btn.disabled : true };
    }""")
    print("Save Changes button:", save_res)
    await asyncio.sleep(2.0)

    # Open Deliverable AutoQC accordion if needed
    acc_res = await task_page.evaluate("""() => {
        const els = Array.from(document.querySelectorAll('*')).filter(el => {
            return (el.innerText || '').trim() === 'Deliverable AutoQC' && el.children.length === 0;
        });
        if (els.length > 0) {
            els[0].parentElement.click();
            return { clicked_accordion: true };
        }
        return { clicked_accordion: false };
    }""")
    print("AutoQC accordion:", acc_res)
    await asyncio.sleep(1.5)

    # Check available buttons and click Run AutoQC / Rerun 1 failing
    run_res = await task_page.evaluate("""() => {
        const btns = Array.from(document.querySelectorAll('button'));
        
        // Priority 1: Rerun 1 failing (fast, targeted)
        const rerunFailBtn = btns.find(b => b.innerText.trim() === 'Rerun 1 failing');
        if (rerunFailBtn) {
            rerunFailBtn.click();
            return { action: 'clicked_rerun_1_failing' };
        }

        // Priority 2: Run AutoQC
        const runBtn = btns.find(b => b.innerText.trim() === 'Run AutoQC');
        if (runBtn) {
            runBtn.click();
            return { action: 'clicked_run_autoqc' };
        }

        return { action: 'none_found', btns: btns.map(b => b.innerText.trim()).filter(Boolean) };
    }""")
    print("Action taken:", run_res)

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
