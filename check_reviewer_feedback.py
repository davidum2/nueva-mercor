import asyncio
import os
from playwright.async_api import async_playwright

async def main():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [p for ctx in browser.contexts for p in ctx.pages if 'mercor.com' in p.url][0]

    clicked = await page.evaluate('''() => {
        const btns = Array.from(document.querySelectorAll('button, [role="tab"], a, div'));
        const fb = btns.find(b => b.innerText && b.innerText.trim() === 'Reviewer Feedback');
        if (fb) {
            fb.click();
            return true;
        }
        return false;
    }''')
    print('Clicked Reviewer Feedback:', clicked)
    await asyncio.sleep(2.0)
    text = await page.evaluate('document.body.innerText')
    with open('task_74b080f5a1554daaba2595c070f210f7/reviewer_feedback_tab.txt', 'w', encoding='utf-8') as f:
        f.write(text)
    print('Guardado reviewer_feedback_tab.txt')

if __name__ == "__main__":
    asyncio.run(main())
