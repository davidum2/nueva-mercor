import asyncio
import os
from playwright.async_api import async_playwright

async def main():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [p for ctx in browser.contexts for p in ctx.pages if 'mercor.com' in p.url][0]

    # Click Show more under Model B
    try:
        await page.locator('button', has_text='Show more').first.click()
    except Exception as e:
        print("Show more click error:", e)

    await asyncio.sleep(1.0)
    
    # Extract Final Answer
    fa = await page.evaluate('''() => {
        const headings = Array.from(document.querySelectorAll('*')).filter(el => el.innerText?.trim() === 'FINAL ANSWER');
        if (headings.length > 0) {
            return headings[0].parentElement ? headings[0].parentElement.innerText : '';
        }
        return '';
    }''')

    with open('task_74b080f5a1554daaba2595c070f210f7/model_b/final_answer_full.txt', 'w', encoding='utf-8') as f:
        f.write(fa)
    print("Guardado model_b/final_answer_full.txt:")
    print(fa[:300])

    # Click DIFF
    await page.locator('button', has_text='DIFF').click()
    await asyncio.sleep(2.0)
    diff_text = await page.evaluate('''() => {
        const monaco = window.monaco;
        if (monaco && monaco.editor) {
            const diffEditors = monaco.editor.getDiffEditors ? monaco.editor.getDiffEditors() : [];
            if (diffEditors.length > 0) {
                return diffEditors[0].getModel().modified.getValue();
            }
        }
        const pre = document.querySelector('pre');
        return pre ? pre.innerText : '';
    }''')

    with open('task_74b080f5a1554daaba2595c070f210f7/model_b/diff.patch', 'w', encoding='utf-8') as f:
        f.write(diff_text)
    print(f"Guardado model_b/diff.patch ({len(diff_text)} chars)")

if __name__ == "__main__":
    asyncio.run(main())
