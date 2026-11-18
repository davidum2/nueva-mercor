import asyncio
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_f5ba2eb1464a4db2831f60a63283341d'

async def dump_pres():
    p = await async_playwright().start()
    b = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [pg for pg in b.contexts[0].pages if TASK_ID in pg.url and 'rubric' not in pg.url][0]
    
    pres = await page.evaluate('''() => {
        return Array.from(document.querySelectorAll('pre, code')).map((el, i) => ({
            index: i,
            tag: el.tagName,
            len: el.innerText.length,
            snippet: el.innerText.substring(0, 300)
        }));
    }''')
    for pr in pres:
        print(f"[{pr['index']}] {pr['tag']} ({pr['len']} chars): {repr(pr['snippet'][:120])}")
    await b.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(dump_pres())
