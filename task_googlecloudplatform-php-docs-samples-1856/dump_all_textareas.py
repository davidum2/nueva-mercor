import asyncio
import json
from playwright.async_api import async_playwright

async def inspect():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [pg for ctx in browser.contexts for pg in ctx.pages if 'task_a6c04444' in pg.url and 'sign-in' not in pg.url][0]
    
    tas = await page.evaluate('''() => {
        const textareas = Array.from(document.querySelectorAll('textarea'));
        return textareas.map((ta, idx) => {
            let label = '';
            let el = ta;
            for (let i = 0; i < 5; i++) {
                if (el.parentElement) {
                    const text = el.parentElement.innerText || '';
                    const lines = text.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
                    if (lines.length > 0) {
                        label = lines[0];
                        break;
                    }
                    el = el.parentElement;
                }
            }
            return {
                idx,
                label: label.slice(0, 80),
                valLen: ta.value.length,
                valPreview: ta.value.slice(0, 60),
                id: ta.id,
                name: ta.name
            };
        });
    }''')
    
    with open('textareas_dump.json', 'w', encoding='utf-8') as f:
        json.dump(tas, f, indent=2, ensure_ascii=False)
    
    print(f"Total textareas found: {len(tas)}")
    for t in tas:
        # safe ascii print
        safe_lbl = t['label'].encode('ascii', 'replace').decode('ascii')
        safe_val = t['valPreview'].encode('ascii', 'replace').decode('ascii')
        print(f"[{t['idx']:02d}] len={t['valLen']:3d} | Label: {safe_lbl[:40]} | Preview: {safe_val[:30]}")

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(inspect())
