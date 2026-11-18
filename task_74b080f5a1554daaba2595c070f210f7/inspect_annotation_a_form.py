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

    # Click ANNOTATION A button
    click_res = await mercor_page.evaluate("""() => {
        const btn = Array.from(document.querySelectorAll('button')).find(b => (b.innerText || '').trim() === 'ANNOTATION A');
        if (btn) {
            btn.click();
            return { clicked: true };
        }
        return { clicked: false };
    }""")
    print("Click ANNOTATION A:", click_res)
    await asyncio.sleep(1.0)

    # Now inspect comboboxes and textareas for A
    info = await mercor_page.evaluate("""() => {
        const combos = Array.from(document.querySelectorAll('[role="combobox"]')).map((b, i) => {
            const parent = b.closest('div')?.parentElement?.parentElement;
            return {
                idx: i,
                text: (b.innerText || '').trim(),
                label: (parent?.innerText || '').slice(0, 80).split('\\n').join(' ')
            };
        });

        const tas = Array.from(document.querySelectorAll('textarea')).map((ta, i) => {
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
            return {
                idx: i,
                label: label.split('\\n').join(' '),
                valPreview: ta.value.slice(0, 100).split('\\n').join(' ')
            };
        });

        return { combos: combos.filter(c => c.label.includes('Rubric') || c.label.includes('Dimension') || c.label.includes('answer')), tas };
    }""")

    print(f"Combos for A ({len(info['combos'])}):")
    for c in info['combos']:
        print(f"  [{c['idx']}] '{c['text']}' -> {c['label']}")

    print(f"Textareas for A ({len(info['tas'])}):")
    for t in info['tas']:
        print(f"  [{t['idx']}] {t['label']} -> {t['valPreview']}")

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
