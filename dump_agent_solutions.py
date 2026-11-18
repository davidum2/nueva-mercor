import asyncio
import os
from playwright.async_api import async_playwright

async def main():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [p for ctx in browser.contexts for p in ctx.pages if 'mercor.com' in p.url][0]

    # Click Agent Solution A
    print("Clicking Agent solution A...")
    await page.locator('button, [role="tab"], div').filter(has_text="Agent solution A").first.click()
    await asyncio.sleep(2.0)
    sol_a = await page.evaluate('document.body.innerText')
    with open('task_74b080f5a1554daaba2595c070f210f7/solution_a_full.txt', 'w', encoding='utf-8') as f:
        f.write(sol_a)
    print(f"Saved solution_a_full.txt ({len(sol_a)} chars)")

    # Click Agent Solution B
    print("Clicking Agent solution B...")
    await page.locator('button, [role="tab"], div').filter(has_text="Agent solution B").first.click()
    await asyncio.sleep(2.0)
    sol_b = await page.evaluate('document.body.innerText')
    with open('task_74b080f5a1554daaba2595c070f210f7/solution_b_full.txt', 'w', encoding='utf-8') as f:
        f.write(sol_b)
    print(f"Saved solution_b_full.txt ({len(sol_b)} chars)")

if __name__ == "__main__":
    asyncio.run(main())
