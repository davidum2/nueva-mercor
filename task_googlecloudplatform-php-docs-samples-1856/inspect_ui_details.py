import asyncio
from playwright.async_api import async_playwright

async def inspect_ui():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    
    # 1. Rubric page scrolled down
    rpages = [pg for pg in browser.contexts[0].pages if 'rubric' in pg.url and 'task_a6c044440a2b440a9d578ad5c375ad94' in pg.url]
    if rpages:
        rpage = rpages[0]
        await rpage.evaluate("window.scrollTo(0, 1000)")
        await asyncio.sleep(1)
        await rpage.screenshot(path='rubric_scrolled_down.png')
        
        # Scroll right on the table container
        await rpage.evaluate("""() => {
            const containers = document.querySelectorAll('*');
            for (const c of containers) {
                if (c.scrollWidth > c.clientWidth + 50) {
                    c.scrollLeft = 800;
                }
            }
        }""")
        await asyncio.sleep(1)
        await rpage.screenshot(path='rubric_scrolled_right.png')
        print("Rubric screenshots saved.")

    # 2. Task page (inspect dimension textareas)
    tpages = [pg for pg in browser.contexts[0].pages if 'rubric' not in pg.url and 'task_a6c044440a2b440a9d578ad5c375ad94' in pg.url and 'sign-in' not in pg.url]
    if tpages:
        tpage = tpages[0]
        # Check textareas values on task page
        field_vals = await tpage.evaluate("""() => {
            const textareas = document.querySelectorAll('textarea');
            return Array.from(textareas).map(t => ({
                id: t.id,
                name: t.name,
                placeholder: t.placeholder,
                val: t.value.slice(0, 60)
            }));
        }""")
        print(f"Task page textareas found: {len(field_vals)}")
        for f in field_vals[:5]:
            print(" ", f)
        await tpage.screenshot(path='task_overview.png')
        print("Task overview screenshot saved.")

    await p.stop()

if __name__ == '__main__':
    asyncio.run(inspect_ui())
