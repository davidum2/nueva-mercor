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

    print("Connected to Mercor page:", mercor_page.url)

    # 1. Expand Rubric accordion if needed
    expanded = await mercor_page.evaluate("""() => {
        const table = document.querySelector('[data-cell="1-1"]');
        if (table) return true;
        const els = Array.from(document.querySelectorAll('*')).filter(el => {
            return (el.innerText || '').trim() === 'RUBRIC' && el.children.length === 0;
        });
        if (els.length > 0) {
            els[0].parentElement.click();
            return true;
        }
        return false;
    }""")
    print("Accordion expanded:", expanded)
    await asyncio.sleep(1.0)

    # 2. Update Criteria for Rubric 2 (data-cell="1-1")
    print("Updating Rubric 2 Criteria...")
    cell_r2 = mercor_page.locator('[data-cell="1-1"]')
    await cell_r2.scroll_into_view_if_needed()
    await cell_r2.click()
    await mercor_page.keyboard.press('Enter')
    await asyncio.sleep(0.3)
    
    # In edit mode, update textarea
    new_r2_criteria = "Does the test reconstruction in CompactSpawnLogContextTest handle all output categories when both missing_path and wrong-type outputs are declared?"
    await mercor_page.evaluate("""(val) => {
        const cell = document.querySelector('[data-cell="1-1"]');
        const ta = cell ? cell.querySelector('textarea') : document.activeElement;
        if (ta && ta.tagName === 'TEXTAREA') {
            const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
            setter.call(ta, val);
            ta.dispatchEvent(new Event('input', { bubbles: true }));
            ta.dispatchEvent(new Event('change', { bubbles: true }));
        }
    }""", new_r2_criteria)
    await asyncio.sleep(0.3)
    # Commit edit by clicking outside or pressing Escape/Tab
    await mercor_page.keyboard.press('Escape')
    await asyncio.sleep(0.5)

    # 3. Update Criteria for Rubric 8 (data-cell="7-1")
    print("Updating Rubric 8 Criteria...")
    cell_r8 = mercor_page.locator('[data-cell="7-1"]')
    await cell_r8.scroll_into_view_if_needed()
    await cell_r8.click()
    await mercor_page.keyboard.press('Enter')
    await asyncio.sleep(0.3)
    
    new_r8_criteria = "Does the change avoid adding unrequested fields to proto messages other than File and Output (such as leaving ExecLogEntry.File without symlink fields)?"
    await mercor_page.evaluate("""(val) => {
        const cell = document.querySelector('[data-cell="7-1"]');
        const ta = cell ? cell.querySelector('textarea') : document.activeElement;
        if (ta && ta.tagName === 'TEXTAREA') {
            const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
            setter.call(ta, val);
            ta.dispatchEvent(new Event('input', { bubbles: true }));
            ta.dispatchEvent(new Event('change', { bubbles: true }));
        }
    }""", new_r8_criteria)
    await asyncio.sleep(0.3)
    await mercor_page.keyboard.press('Escape')
    await asyncio.sleep(0.5)

    # 4. Update Source for Rubric 15 (data-cell="14-3") -> COMMON_ENGINEERING_KNOWLEDGE
    print("Updating Rubric 15 Source...")
    cell_r15_source = mercor_page.locator('[data-cell="14-3"]')
    await cell_r15_source.scroll_into_view_if_needed()
    await cell_r15_source.click()
    await asyncio.sleep(0.3)
    await mercor_page.keyboard.press('Enter')
    await asyncio.sleep(0.5)

    # Click COMMON_ENGINEERING_KNOWLEDGE in popover
    await mercor_page.evaluate("""() => {
        const items = Array.from(document.querySelectorAll('[role="option"]'));
        const target = items.find(it => it.innerText && it.innerText.includes('COMMON_ENGINEERING_KNOWLEDGE'));
        if (target) {
            target.click();
            return true;
        }
        return false;
    }""")
    await asyncio.sleep(0.5)

    # 5. Update Textareas in Right Sidebar:
    # Textarea #18: Rubric 2 Reason B (typos fixed)
    # Textarea #22: Rubric 6 Reason B (typo fixed)
    print("Updating textareas for Rubric 2 and Rubric 6 Reason B...")
    new_r2_reason_b = "No. Model B introduces invalid_output_path in ExecLogEntry.Output and preserves missing_path as a sibling field. The updated test suite reconstruction in CompactSpawnLogContextTest.java does not handle all coexisting output cases without an unhandled branch."
    new_r6_reason_b = "In step 39, Model B added replacement test cases in SpawnLogContextTestBase.java, specifically introducing testFileOutput_wrongType to cover the directory-as-file mismatch scenario previously handled by testDirectoryOutput. The execution logs in step 61 (test.xml) confirm that testFileOutput_wrongType[WITHOUT_BYTES] and testFileOutput_wrongType[WITH_BYTES] were compiled, executed, and passed."

    await mercor_page.evaluate("""({ r2, r6 }) => {
        const tas = Array.from(document.querySelectorAll('textarea'));
        const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
        
        // Find by label or index
        for (let i = 0; i < tas.length; i++) {
            const ta = tas[i];
            const p = ta.closest('div');
            const label = p ? p.innerText : '';
            if (label.includes('Rubric 2 · reason (B)') || i === 18) {
                setter.call(ta, r2);
                ta.dispatchEvent(new Event('input', { bubbles: true }));
                ta.dispatchEvent(new Event('change', { bubbles: true }));
            }
            if (label.includes('Rubric 6 · reason (B)') || i === 22) {
                setter.call(ta, r6);
                ta.dispatchEvent(new Event('input', { bubbles: true }));
                ta.dispatchEvent(new Event('change', { bubbles: true }));
            }
        }
    }""", { 'r2': new_r2_reason_b, 'r6': new_r6_reason_b })
    await asyncio.sleep(0.5)

    # 6. Update Task Type dropdown if needed (Bug Fix Deterministic)
    print("Checking and updating Task Type...")
    await mercor_page.evaluate("""() => {
        // Find Task Type trigger
        const triggers = Array.from(document.querySelectorAll('[role="combobox"]'));
        const tt = triggers.find(t => {
            const p = t.closest('div');
            return p && (p.innerText.includes('Task type') || p.innerText.includes('Classify the task'));
        });
        if (tt && !tt.innerText.includes('Deterministic')) {
            tt.click();
        }
    }""")
    await asyncio.sleep(0.5)
    # Select option if open
    await mercor_page.evaluate("""() => {
        const options = Array.from(document.querySelectorAll('[role="option"]'));
        const det = options.find(o => o.innerText.includes('Deterministic') || o.innerText.includes('bug_fix_deterministic'));
        if (det) det.click();
    }""")
    await asyncio.sleep(0.5)

    # 7. Click Save Changes button
    print("Clicking Save Changes...")
    save_result = await mercor_page.evaluate("""() => {
        const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.trim() === 'Save Changes');
        if (btn) {
            btn.click();
            return { found: true, disabled: btn.disabled };
        }
        return { found: false };
    }""")
    print("Save Changes button:", save_result)
    await asyncio.sleep(3.0)

    # 8. Trigger AutoQC rerun
    print("Triggering AutoQC rerun...")
    rerun_result = await mercor_page.evaluate("""() => {
        // First try clicking 'Rerun 3 failing' or 'Run AutoQC'
        const btns = Array.from(document.querySelectorAll('button'));
        const rerunBtn = btns.find(b => b.innerText.includes('Rerun 3 failing') || b.innerText.includes('Run AutoQC'));
        if (rerunBtn) {
            rerunBtn.click();
            return { clicked: true, text: rerunBtn.innerText };
        }
        return { clicked: false };
    }""")
    print("AutoQC rerun clicked:", rerun_result)

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
