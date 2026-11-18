import asyncio
import json
from playwright.async_api import async_playwright

async def inspect():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [pg for ctx in browser.contexts for pg in ctx.pages if 'task_a6c04444' in pg.url and 'sign-in' not in pg.url][0]

    # Navigate to Rubric tab
    await page.evaluate('''() => {
        const btns = Array.from(document.querySelectorAll('button, li, [role="tab"]'));
        const rubTab = btns.find(b => (b.innerText || '').trim().includes('Rubric (create)') || (b.innerText || '').trim() === 'Rubric');
        if (rubTab) rubTab.click();
    }''')
    await asyncio.sleep(2.0)

    # Inspect the rubric table or form elements
    info = await page.evaluate('''() => {
        const textareas = Array.from(document.querySelectorAll('textarea')).map((ta, idx) => ({
            idx,
            placeholder: ta.placeholder,
            value: ta.value.slice(0, 50),
            name: ta.name,
            id: ta.id,
            className: ta.className
        }));
        
        const inputs = Array.from(document.querySelectorAll('input')).map((inp, idx) => ({
            idx,
            type: inp.type,
            value: inp.value,
            placeholder: inp.placeholder,
            name: inp.name,
            id: inp.id
        }));

        const selects = Array.from(document.querySelectorAll('select')).map((sel, idx) => ({
            idx,
            value: sel.value,
            options: Array.from(sel.options).map(o => o.text)
        }));

        const buttons = Array.from(document.querySelectorAll('button')).map(b => (b.innerText || '').trim()).filter(t => t.length > 0 && t.length < 40);

        return {
            textareasCount: textareas.length,
            textareas: textareas.slice(0, 15),
            inputsCount: inputs.length,
            inputs: inputs.filter(i => i.value || i.placeholder),
            selectsCount: selects.length,
            selects,
            buttonsCount: buttons.length,
            buttonsSample: buttons.slice(0, 20)
        };
    }''')

    print(json.dumps(info, indent=2))

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(inspect())
