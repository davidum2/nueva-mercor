import asyncio
import json
from playwright.async_api import async_playwright

async def main():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [p for ctx in browser.contexts for p in ctx.pages if 'mercor.com' in p.url][0]

    textareas = await page.evaluate('''() => {
        return Array.from(document.querySelectorAll('textarea')).map((el, i) => {
            // Find nearby label or preceding header
            let label = '';
            let parent = el.parentElement;
            for (let k = 0; k < 4 && parent; k++) {
                const labelEl = parent.querySelector('label, h1, h2, h3, h4, h5, h6, .text-sm, .font-medium');
                if (labelEl && labelEl.innerText.trim()) {
                    label = labelEl.innerText.trim();
                    break;
                }
                parent = parent.parentElement;
            }
            return {
                index: i,
                label: label.substring(0, 150),
                value: el.value,
                valueLength: el.value.length
            };
        });
    }''')

    with open('task_74b080f5a1554daaba2595c070f210f7/textareas_full.json', 'w', encoding='utf-8') as f:
        json.dump(textareas, f, indent=2, ensure_ascii=False)

    print(f"Total textareas: {len(textareas)}")
    for t in textareas:
        if t['valueLength'] > 0:
            print(f"Idx {t['index']} | Label: {t['label']} | Len: {t['valueLength']}")
            print(f"Content: {t['value'][:150]}...")
            print("-" * 50)

if __name__ == "__main__":
    asyncio.run(main())
