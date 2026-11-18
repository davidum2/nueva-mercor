import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True)

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def inspect():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    if task_pages:
        page = task_pages[0]
        data = await page.evaluate("""() => {
            const textareas = Array.from(document.querySelectorAll('textarea')).map((t, idx) => {
                let label = '';
                let node = t;
                while (node && node !== document.body) {
                    const prev = node.previousElementSibling;
                    if (prev && prev.innerText && prev.innerText.trim().length > 0) {
                        label = prev.innerText.trim().replace(/\\n/g, ' ').slice(0, 80);
                        break;
                    }
                    if (node.parentElement && node.parentElement.querySelector('label')) {
                        label = node.parentElement.querySelector('label').innerText.trim().replace(/\\n/g, ' ').slice(0, 80);
                        break;
                    }
                    node = node.parentElement;
                }
                return {
                    idx,
                    len: t.value.length,
                    val: t.value.slice(0, 60),
                    label
                };
            });

            // Find where 'Comparative Rationale' is in document text
            const headings = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, h6, label, div, span, p'))
                .filter(el => el.innerText && el.innerText.includes('Comparative Rationale'))
                .map(el => ({
                    tag: el.tagName,
                    text: el.innerText.trim().slice(0, 100),
                    nextEl: el.nextElementSibling ? el.nextElementSibling.tagName : null
                }));

            return { textareas, headings };
        }""")

        print(f"Total Textareas: {len(data['textareas'])}")
        for t in data['textareas']:
            print(f"  [{t['idx']:02d}] len={t['len']:4d} | label: {t['label']} | val: {t['val']}")

        print(f"\nHeadings/Elements with 'Comparative Rationale': {len(data['headings'])}")
        for h in data['headings'][:10]:
            print(f"  <{h['tag']}> {h['text']} (next: {h['nextEl']})")

    await p.stop()

if __name__ == '__main__':
    asyncio.run(inspect())
