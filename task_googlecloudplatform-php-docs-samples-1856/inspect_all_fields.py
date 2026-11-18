import asyncio
import json
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True)

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def inspect_all_fields():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]
    
    result = await page.evaluate("""() => {
        const textareas = Array.from(document.querySelectorAll('textarea'));
        return textareas.map((t, idx) => {
            const key = Object.keys(t).find(k => k.startsWith('__reactFiber$'));
            let cur = key ? t[key] : null;
            let fieldId = null;
            let label = null;
            while (cur) {
                if (cur.memoizedProps && cur.memoizedProps.fieldDef) {
                    fieldId = cur.memoizedProps.fieldDef.field_id;
                    label = cur.memoizedProps.fieldDef.name || cur.memoizedProps.fieldDef.label;
                    break;
                }
                cur = cur.return;
            }
            return {
                idx,
                fieldId,
                label,
                valLen: t.value.length,
                valSnippet: t.value.slice(0, 40)
            };
        });
    }""")
    
    print("All Textareas and their fieldDef:")
    for r in result:
        print(f"  [{r['idx']:02d}] field_id={r['fieldId']} | label={r['label']} | len={r['valLen']} | {r['valSnippet']}")
        
    await p.stop()

if __name__ == '__main__':
    asyncio.run(inspect_all_fields())
