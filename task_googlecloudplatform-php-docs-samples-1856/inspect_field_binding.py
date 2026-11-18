import asyncio
import json
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True)

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def inspect_field_binding():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]
    
    result = await page.evaluate("""() => {
        const t = document.querySelectorAll('textarea')[30];
        const key = Object.keys(t).find(k => k.startsWith('__reactFiber$'));
        let cur = key ? t[key] : null;
        let info = [];
        while (cur) {
            if (cur.memoizedProps) {
                const mp = cur.memoizedProps;
                for (const k of Object.keys(mp)) {
                    if (typeof mp[k] === 'string' && (mp[k].startsWith('field_') || mp[k].includes('rationale') || mp[k].includes('comparative'))) {
                        info.push({ from: 'props', key: k, val: mp[k] });
                    }
                    if (typeof mp[k] === 'object' && mp[k] !== null) {
                        for (const subK of Object.keys(mp[k])) {
                            if (typeof mp[k][subK] === 'string' && (mp[k][subK].startsWith('field_') || mp[k][subK].includes('rationale'))) {
                                info.push({ from: `props.${k}`, key: subK, val: mp[k][subK] });
                            }
                        }
                    }
                }
            }
            cur = cur.return;
        }
        return info;
    }""")
    
    print("Binding info:")
    for inf in result:
        print(" ", inf)
        
    await p.stop()

if __name__ == '__main__':
    asyncio.run(inspect_field_binding())
