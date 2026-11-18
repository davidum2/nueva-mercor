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

    if not mercor_page:
        print("No mercor page found")
        await browser.close()
        await p.stop()
        return

    elements_info = await mercor_page.evaluate("""() => {
        const textareas = Array.from(document.querySelectorAll('textarea')).map((el, i) => {
            // find nearby label or header
            let label = '';
            let p = el.parentElement;
            for (let d = 0; d < 4 && p; d++) {
                const l = p.querySelector('label, [class*="label"], h3, h4, [class*="title"]');
                if (l && l.innerText) {
                    label = l.innerText.trim();
                    break;
                }
                p = p.parentElement;
            }
            return {
                index: i,
                id: el.id,
                name: el.name,
                label: label,
                placeholder: el.placeholder,
                valueLength: el.value ? el.value.length : 0,
                valuePreview: el.value ? el.value.substring(0, 50) : ''
            };
        });

        const inputs = Array.from(document.querySelectorAll('input, select, [role="combobox"]')).map((el, i) => {
            return {
                index: i,
                tagName: el.tagName,
                type: el.type,
                role: el.getAttribute('role'),
                id: el.id,
                name: el.name,
                value: el.value || el.innerText || ''
            };
        });

        return { textareas, inputs };
    }""")

    with open('form_elements_dump.json', 'w', encoding='utf-8') as f:
        json.dump(elements_info, f, indent=2)

    print(f"Total textareas: {len(elements_info['textareas'])}")
    print(f"Total inputs/selects: {len(elements_info['inputs'])}")
    for ta in elements_info['textareas']:
        print(f"Textarea #{ta['index']}: label='{ta['label']}' len={ta['valueLength']} prev='{ta['valuePreview']}'")

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
