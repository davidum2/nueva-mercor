import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def select_much_better():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]
    
    # Click the Pairwise Evaluation dropdown trigger
    trigger = page.locator('button:has-text("A BETTER")')
    count = await trigger.count()
    print("Found triggers:", count)
    if count > 0:
        await trigger.first.click()
        await asyncio.sleep(1)
        
        # Click 'A MUCH BETTER' option
        opt = page.locator('[role="option"]:has-text("A MUCH BETTER"), div:has-text("A MUCH BETTER")')
        opt_count = await opt.count()
        print("Found option count:", opt_count)
        if opt_count > 0:
            await opt.first.click()
            print("Selected A MUCH BETTER!", flush=True)
            await asyncio.sleep(1)
            
    await page.screenshot(path='pairwise_much_better_selected.png')
    print("Saved pairwise_much_better_selected.png")
    await p.stop()

if __name__ == '__main__':
    asyncio.run(select_much_better())
