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

    info = await mercor_page.evaluate("""() => {
        // Find all radio buttons, toggle buttons, or answers for Rubrics
        const buttons = Array.from(document.querySelectorAll('button, input[type="radio"], [role="radio"]'));
        const rubricButtons = buttons.map(b => {
            const parentText = b.closest('div')?.parentElement?.innerText || '';
            return {
                text: (b.innerText || b.value || '').trim(),
                ariaChecked: b.getAttribute('aria-checked'),
                role: b.getAttribute('role'),
                parentSample: parentText.slice(0, 100).replace(/\\n/g, ' ')
            };
        }).filter(b => b.parentSample.includes('Rubric') || b.parentSample.includes('rubric') || b.text === 'YES' || b.text === 'NO');

        // Find Task Type trigger
        const selects = Array.from(document.querySelectorAll('[role="combobox"], select, button')).filter(el => {
            const txt = el.closest('div')?.innerText || '';
            return txt.includes('Task type') || txt.includes('Classify the task');
        }).map(el => ({
            tag: el.tagName,
            text: el.innerText,
            role: el.getAttribute('role'),
            outer: el.outerHTML.slice(0, 150)
        }));

        // Find textareas for rubrics
        const tas = Array.from(document.querySelectorAll('textarea')).map((ta, idx) => {
            const container = ta.closest('div')?.parentElement?.innerText || '';
            return {
                index: idx,
                label: container.slice(0, 80).replace(/\\n/g, ' '),
                valLen: ta.value.length,
                valPreview: ta.value.slice(0, 80).replace(/\\n/g, ' ')
            };
        });

        // Find Before you submit items and their status
        const checklist = Array.from(document.querySelectorAll('*')).filter(el => {
            const txt = (el.innerText || '').trim();
            return (txt === 'Before you submit' || txt.includes('Task type required'));
        }).map(el => ({
            text: el.innerText,
            color: window.getComputedStyle(el).color
        }));

        return { rubricButtons: rubricButtons.slice(0, 40), selects, tas, checklist };
    }""")

    print("Task Type triggers:", json.dumps(info['selects'], indent=2))
    print("Checklist matches:", json.dumps(info['checklist'], indent=2))
    print("Rubric textareas count:", len(info['tas']))
    for t in info['tas']:
        if 'Rubric' in t['label'] or 'rubric' in t['label'] or 'reason' in t['label']:
            print(f"  TA #{t['index']}: {t['label']} -> len={t['valLen']} [{t['valPreview']}]")
    print("Rubric buttons sample:", len(info['rubricButtons']))
    for b in info['rubricButtons'][:15]:
        print(f"  Button: '{b['text']}' checked={b['ariaChecked']} in [{b['parentSample']}]")

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
