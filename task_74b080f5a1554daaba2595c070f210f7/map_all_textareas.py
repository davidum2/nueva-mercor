import asyncio
import json
from playwright.async_api import async_playwright

async def run():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    mercor_page = None
    for ctx in browser.contexts:
        for page in ctx.pages:
            if 'mercor.com' in page.url:
                mercor_page = page
                break
        if mercor_page:
            break

    tas = await mercor_page.evaluate(r"""() => {
        const textareas = Array.from(document.querySelectorAll('textarea'));
        return textareas.map((ta, i) => {
            // Find true label: look up the tree
            let label = '';
            let p = ta.parentElement;
            for (let depth = 0; depth < 5 && p; depth++) {
                const l = p.querySelector('label, [class*="label"], h3, h4');
                if (l && l.innerText.trim()) {
                    label = l.innerText.trim();
                    break;
                }
                p = p.parentElement;
            }
            if (!label && ta.closest('div')?.parentElement) {
                label = ta.closest('div').parentElement.innerText.slice(0, 60);
            }
            return {
                idx: i,
                label: label.split('\n').join(' '),
                valPreview: ta.value.slice(0, 120).split('\n').join(' ')
            };
        });
    }""")

    with open('current_textareas_mapped.json', 'w', encoding='utf-8') as f:
        json.dump(tas, f, indent=2, ensure_ascii=False)

    print(f"Dumped {len(tas)} textareas to current_textareas_mapped.json:")
    for t in tas:
        print(f"  [{t['idx']}] {t['label']} -> {t['valPreview']}")

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
