import asyncio
from playwright.async_api import async_playwright

async def run():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    ctx = browser.contexts[0]
    
    task_page = None
    for pg in ctx.pages:
        if 'task_74b080f5a1554daaba2595c070f210f7/?' in pg.url:
            task_page = pg
            break

    if not task_page:
        print("Task page not found")
        await browser.close()
        await p.stop()
        return

    print("Task page found:", task_page.url)
    print("Reloading task page to fetch updated rubric table...")
    await task_page.reload()
    await asyncio.sleep(4.0)

    # Update textareas on task page
    fix_res = await task_page.evaluate("""() => {
        const tas = Array.from(document.querySelectorAll('textarea'));
        const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
        const modified = [];

        // 1. Restore Adjudication rationale
        const origAdjudication = "Thanks, solid work here, the dimension reasoning is detailed and your entry citations all check out.\\n\\nTwo things to fix.\\n\\n1. Rubric 6 side B should be YES. B did add replacement tests, step 39 adds them and step 61 lists them from test.xml, including `testFileOutput_wrongType`, which covers the case `testDirectoryOutput` used to. As it stands it also contradicts rubric 9's side B reason and your Dimension 7 note about B's six tests.\\n\\n2. That flip puts B at 80% pass rate, so you'll need another item or two that both sides genuinely fail. One candidate is that both keep `missing_path` alongside the new wrong-type field, leaving a category the updated test reconstruction no longer handles.\\n\\nA few small things I already fixed. Dimension 4 side B said \\\"two things\\\" but listed one. Rubric 8's side A reason claimed A never reads the field it added, but its `logSymlink` does. Rubric 5's criterion now points at the accessor the repo's tests expect rather than sibling naming. ";
        if (tas[0] && !tas[0].value.includes('Thanks, solid work here')) {
            setter.call(tas[0], origAdjudication);
            tas[0].dispatchEvent(new Event('input', { bubbles: true }));
            tas[0].dispatchEvent(new Event('change', { bubbles: true }));
            modified.push('restored_adjudication');
        }

        // 2. Fix Dimension 7 Reason B citations
        for (let i = 0; i < tas.length; i++) {
            const val = tas[i].value;
            if (val.includes('entry 194 of its log shows') || val.includes('entry 194 of B')) {
                const fixed = val.replace('entry 194 of its log shows //src/test/java/com/google/devtools/build/lib/exec:ExecTests PASSED in 8.7s and entry 214 shows 37 errors=\\'0\\'', 'the recorded log shows //src/test/java/com/google/devtools/build/lib/exec:ExecTests PASSED in 8.7s under call_129_c and shows 37 errors=\\'0\\' under call_141_c')
                                 .replace('Entry 194 of B\\'s log records //src/test/java/com/google/devtools/build/lib/exec:ExecTests PASSED in 8.7s and entry 214 records 37 errors=\\'0\\'', 'The execution log of Model B records //src/test/java/com/google/devtools/build/lib/exec:ExecTests PASSED in 8.7s under call_129_c and records 37 errors=\\'0\\' under call_141_c');
                setter.call(tas[i], fixed);
                tas[i].dispatchEvent(new Event('input', { bubbles: true }));
                tas[i].dispatchEvent(new Event('change', { bubbles: true }));
                modified.push('fixed_citations_in_ta_' + i);
            }
            if (val.includes('corroborated at entries 194 and 214')) {
                const fixed = val.replace('corroborated at entries 194 and 214 of its own log', 'corroborated under call_129_c and call_141_c of its own log')
                                 .replace('anywhere in its 323 entries', 'anywhere in its recorded trajectory');
                setter.call(tas[i], fixed);
                tas[i].dispatchEvent(new Event('input', { bubbles: true }));
                tas[i].dispatchEvent(new Event('change', { bubbles: true }));
                modified.push('fixed_comparative');
            }
        }

        return modified;
    }""")
    print("Task page textarea updates:", fix_res)
    await asyncio.sleep(1.0)

    # Save Changes
    save_res = await task_page.evaluate("""() => {
        const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.trim() === 'Save Changes');
        if (btn) {
            btn.click();
            return { clicked: true, disabled: btn.disabled };
        }
        return { clicked: false };
    }""")
    print("Save Changes:", save_res)
    await asyncio.sleep(2.0)

    # Run AutoQC
    run_res = await task_page.evaluate("""() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const target = btns.find(b => b.innerText.includes('Run AutoQC') || b.innerText.includes('Rerun'));
        if (target) {
            target.click();
            return { clicked: true, text: target.innerText };
        }
        return { clicked: false, btns: btns.map(b => b.innerText.trim()).filter(t => t.includes('AutoQC') || t.includes('Rerun')) };
    }""")
    print("Run AutoQC:", run_res)

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
