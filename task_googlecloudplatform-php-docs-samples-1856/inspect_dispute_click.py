import asyncio
import sys
import json
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

DISPUTE_REASON = "The verifier reasons for Rubric 2 have been updated to cite the actual API setters present in the codebase: setDeidentifyTemplate, setStructuredDeidentifyTemplate, and setImageRedactTemplate at patch_a.diff:L81-84 and patch_b.diff:L80-83, removing the outdated reference to setDeidentifyTemplateName."

async def test_dispute():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    # Expand DELIVERABLE AUTOQC accordion if needed
    header = page.locator('div.cursor-pointer:has-text("DELIVERABLE AUTOQC")')
    if await header.count() > 0:
        await header.first.scroll_into_view_if_needed()
        # check if already open
        is_open = await page.locator('button:has-text("Dispute")').count() > 0
        if not is_open:
            await header.first.click()
            await asyncio.sleep(2)

    # Click Dispute button
    dispute_btn = page.locator('button:text-is("Dispute")')
    count = await dispute_btn.count()
    print("Found Dispute button count:", count)

    if count > 0:
        await dispute_btn.first.click()
        print("Clicked Dispute button!", flush=True)
        await asyncio.sleep(2)

        # Check what appeared
        ui_state = await page.evaluate('''() => {
            const inputs = Array.from(document.querySelectorAll('textarea, input')).filter(el => {
                const rect = el.getBoundingClientRect();
                return rect.width > 0 && rect.height > 0;
            }).map(el => ({
                tag: el.tagName,
                placeholder: el.placeholder,
                value: el.value,
                className: el.className
            }));

            const popovers = Array.from(document.querySelectorAll('[role="dialog"], [role="popover"], div.popover, div[data-state="open"]')).map(d => d.innerText);

            return { inputs, popovers };
        }''')

        print("UI state after clicking Dispute:", json.dumps(ui_state, indent=2))
        await page.screenshot(path='after_dispute_click.png')
        print("Saved after_dispute_click.png")

    await p.stop()

if __name__ == '__main__':
    asyncio.run(test_dispute())
