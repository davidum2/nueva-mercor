import asyncio
from playwright.async_api import async_playwright

async def switch_b():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [pg for ctx in browser.contexts for pg in ctx.pages if 'task_a6c04444' in pg.url and 'sign-in' not in pg.url][0]

    # Use real Playwright click
    print("Clicking Model B tab using Playwright locator...")
    tab_b = page.locator('button[role="tab"]').filter(has_text="Model B")
    await tab_b.click()
    await asyncio.sleep(2.0)

    # Check active state
    state = await page.evaluate("""() => {
        const tabs = Array.from(document.querySelectorAll('button[role="tab"]')).filter(t => ['Model A', 'Model B'].includes((t.innerText || '').trim()));
        return tabs.map(t => ({ text: t.innerText.trim(), state: t.getAttribute('data-state'), ariaSelected: t.getAttribute('aria-selected') }));
    }""")
    print('Tabs after click:', state)

    # Open LOGS collapsible if closed
    logs_trigger = page.locator('button[data-slot="collapsible-trigger"]').filter(has_text="LOGS")
    trigger_state = await logs_trigger.get_attribute("data-state")
    print(f"LOGS trigger state in Model B: {trigger_state}")
    if trigger_state == "closed":
        await logs_trigger.click()
        await asyncio.sleep(2.0)

    # Click Expand all if present
    exp_btn = page.locator('button').filter(has_text="Expand all")
    if await exp_btn.count() > 0 and await exp_btn.first.is_visible():
        await exp_btn.first.click()
        print("Clicked Expand all in Model B")
        await asyncio.sleep(2.0)

    # Click more lines buttons
    total_clicked = 0
    for r in range(15):
        clicked = await page.evaluate("""() => {
            const btns = Array.from(document.querySelectorAll('button')).filter(b => {
                const t = (b.innerText || '').toLowerCase();
                return t.includes('more lines') || t.includes('show more');
            });
            btns.forEach(b => {
                try { b.click(); } catch(e) {}
            });
            return btns.length;
        }""")
        print(f"Round {r}: Clicked {clicked} more buttons in Model B")
        total_clicked += clicked
        if clicked == 0:
            break
        await asyncio.sleep(2.0)

    print(f"Total more buttons clicked in Model B: {total_clicked}")

    # Extract text
    text = await page.evaluate('document.body.innerText')
    out_file = r"c:\desarrollo\nueva-mercor\task_googlecloudplatform-php-docs-samples-1856\model_b\all_steps_expanded.txt"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Saved {out_file} with {len(text)} characters.")

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(switch_b())
