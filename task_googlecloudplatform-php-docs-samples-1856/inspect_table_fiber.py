import asyncio
import json
from playwright.async_api import async_playwright

async def inspect():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    ctx = browser.contexts[0]
    
    old_rubric = [pg for pg in ctx.pages if 'task_74b' in pg.url and '/rubric/' in pg.url][0]

    props_info = await old_rubric.evaluate('''() => {
        const table = document.querySelector('table');
        if (!table) return { error: 'no table' };
        
        const k = Object.keys(table).find(key => key.startsWith('__reactFiber$'));
        let f = table[k];
        let depth = 0;
        let found = [];
        while (f && depth < 25) {
            const p = f.memoizedProps;
            if (p) {
                const keys = Object.keys(p);
                if (keys.some(k => ['data', 'rows', 'items', 'rubric', 'rubrics', 'table', 'value', 'onChange'].includes(k))) {
                    found.push({
                        depth,
                        keys,
                        dataPreview: p.data ? (Array.isArray(p.data) ? `Array(${p.data.length})` : typeof p.data) : null,
                        itemsPreview: p.items ? (Array.isArray(p.items) ? `Array(${p.items.length})` : typeof p.items) : null,
                        rubricPreview: p.rubric ? Object.keys(p.rubric) : null,
                        sampleRow: p.data && p.data[0] ? p.data[0] : (p.items && p.items[0] ? p.items[0] : null)
                    });
                }
            }
            f = f.return;
            depth++;
        }
        return found;
    }''')

    print("React Fiber props for Table in task_74b:")
    print(json.dumps(props_info, indent=2))

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(inspect())
