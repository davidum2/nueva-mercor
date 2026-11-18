import asyncio
import json
from playwright.async_api import async_playwright

async def inspect_all():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page0 = browser.contexts[0].pages[0]

    # Dump all elements with text containing "Rubric" or "ANNOTATION"
    data = await page0.evaluate("""() => {
        const sections = Array.from(document.querySelectorAll('section, [role="region"], div[class*="section"], div[class*="tab"]')).map(s => {
            const h = s.querySelector('h1, h2, h3, h4, [class*="header"], [class*="title"]');
            return h ? h.innerText.trim() : '';
        }).filter(Boolean);

        // Find all radio, combobox, textarea, inputs
        const inputs = Array.from(document.querySelectorAll('textarea, [role="combobox"], input')).map((el, i) => {
            let p = el.parentElement;
            let label = '';
            for (let depth = 0; depth < 5 && p; depth++) {
                const l = p.querySelector('label, [class*="label"], h3, h4');
                if (l && l.innerText.trim()) {
                    label = l.innerText.trim();
                    break;
                }
                p = p.parentElement;
            }
            if (!label && el.closest('div')?.parentElement) {
                label = el.closest('div').parentElement.innerText.slice(0, 80);
            }
            return {
                idx: i,
                tag: el.tagName,
                type: el.type,
                role: el.getAttribute('role'),
                label: label.split('\\n').join(' '),
                val: (el.value || el.innerText || '').slice(0, 80).split('\\n').join(' ')
            };
        });

        return { sections: Array.from(new Set(sections)), inputs };
    }""")

    with open('page0_all_inputs_dump.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Dumped {len(data['inputs'])} inputs on Page 0 to page0_all_inputs_dump.json")
    for item in data['inputs']:
        if any(k in item['label'] for k in ['Rubric', 'answer', 'reason', 'Quality']):
            print(f"[{item['idx']}] {item['tag']} ({item['role'] or item['type']}) | {item['label'][:60]} -> {item['val']}")

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(inspect_all())
