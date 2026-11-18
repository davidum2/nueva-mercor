import asyncio
import json
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def check_ui():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    # Close any popups
    await page.keyboard.press("Escape")
    await asyncio.sleep(0.5)

    data = await page.evaluate('''() => {
        const buttons = Array.from(document.querySelectorAll('button')).map(b => ({
            text: b.innerText ? b.innerText.trim() : '',
            disabled: b.disabled,
            visible: b.offsetParent !== null,
            classes: b.className
        }));
        return {
            buttons: buttons.filter(b => b.text.length > 0 && b.text.length < 50),
            title: document.title,
            url: window.location.href
        };
    }''')

    print("Buttons found:")
    for b in data['buttons']:
        if any(w in b['text'].lower() for w in ['autoqc', 'run', 'submit', 'nav', 'failing', 'review']):
            print(" ->", b)

    await page.screenshot(path='current_screen_now.png')
    print("Screenshot saved to current_screen_now.png")
    await p.stop()

if __name__ == '__main__':
    asyncio.run(check_ui())
