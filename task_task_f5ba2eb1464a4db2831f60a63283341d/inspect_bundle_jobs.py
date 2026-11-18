import asyncio
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_f5ba2eb1464a4db2831f60a63283341d'
TASK_DIR = os.path.join(r'c:\desarrollo\nueva-mercor', f'task_{TASK_ID}')

async def inspect_jobs():
    p = await async_playwright().start()
    b = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [pg for pg in b.contexts[0].pages if TASK_ID in pg.url and 'rubric' not in pg.url][0]

    # In bundle explorer, click on job.log or trial.log
    jobs_info = await page.evaluate('''() => {
        const btns = Array.from(document.querySelectorAll('button')).map(b => (b.innerText || '').trim());
        return btns.filter(t => t.includes('job.log') || t.includes('trial.log') || t.includes('electerm-electerm-4191__') || t.includes('test-stdout.txt'));
    }''')
    print("Found job buttons:", jobs_info)

    # Let's read trial.log or job.log by clicking them
    for target in ['job.log', 'trial.log', 'test-stdout.txt']:
        clicked = await page.evaluate(f'''(fn) => {{
            const btns = Array.from(document.querySelectorAll('button'));
            const target = btns.find(b => (b.innerText || '').trim() === fn);
            if (target) {{
                target.scrollIntoView({{ block: 'center' }});
                target.click();
                return true;
            }}
            return false;
        }}''', target)
        if clicked:
            await asyncio.sleep(1)
            content = await page.evaluate('''() => {
                if (window.monaco && window.monaco.editor) {
                    const models = window.monaco.editor.getModels();
                    if (models.length > 0) {
                        return models[models.length - 1].getValue();
                    }
                }
                const editorEl = document.querySelector('.monaco-editor');
                return editorEl ? editorEl.innerText : null;
            }''')
            print(f"Content for {target} (len={len(content) if content else 0}):")
            if content:
                print(content[:500])
                print("-" * 50)

    await b.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(inspect_jobs())
