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

    accordions = await mercor_page.evaluate("""() => {
        // Find all accordion headers or collapsible sections
        const headers = Array.from(document.querySelectorAll('*')).filter(el => {
            const t = (el.innerText || '').trim();
            return t.startsWith('Annotation A') || t.startsWith('Annotation B') || t.startsWith('ANNOTATION A') || t.startsWith('ANNOTATION B');
        });
        return headers.map(h => ({
            tag: h.tagName,
            text: h.innerText.split('\\n')[0],
            parentText: h.parentElement?.innerText.slice(0, 100).split('\\n').join(' ')
        }));
    }""")
    print("Accordions:", json.dumps(accordions, indent=2))

    # Try clicking the 'Annotation A' div
    expand_a = await mercor_page.evaluate("""() => {
        const els = Array.from(document.querySelectorAll('div, span, button')).filter(el => {
            const t = (el.innerText || '').trim();
            return t === 'Annotation A' && el.children.length === 0;
        });
        if (els.length > 0) {
            els[0].click();
            return { clicked: true, tag: els[0].tagName };
        }
        return { clicked: false, count: els.length };
    }""")
    print("Expand Annotation A:", expand_a)
    await asyncio.sleep(1.0)

    # Now check if answer (A) appears
    has_a = await mercor_page.evaluate("""() => {
        const text = document.body.innerText;
        return {
            hasAnswerA: text.includes('Rubric 1 · answer (A)') || text.includes('Rubric 2 · answer (A)'),
            hasAnswerB: text.includes('Rubric 1 · answer (B)')
        };
    }""")
    print("Has Answer A after click:", has_a)

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
