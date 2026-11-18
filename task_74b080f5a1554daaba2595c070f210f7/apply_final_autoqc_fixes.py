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

    # -------------------------------------------------------------
    # Helper to edit a text cell in the Task Rubric spreadsheet
    # -------------------------------------------------------------
    async def edit_text_cell(row, col, new_value):
        cell_sel = f'[data-cell="{row}-{col}"]'
        res = await mercor_page.evaluate("""({ sel, val }) => {
            const cell = document.querySelector(sel);
            if (!cell) return { error: 'not found: ' + sel };
            cell.scrollIntoView({ block: 'center' });

            const key = Object.keys(cell).find(k => k.startsWith('__reactFiber$'));
            let f = cell[key];
            if (f && f.memoizedProps.onDoubleClick) {
                f.memoizedProps.onDoubleClick({ preventDefault: () => {}, stopPropagation: () => {} });
            }
            return { dblclicked: true };
        }""", { 'sel': cell_sel, 'val': new_value })
        
        await asyncio.sleep(0.4)
        
        set_res = await mercor_page.evaluate("""({ sel, val }) => {
            const cell = document.querySelector(sel);
            const ta = cell ? cell.querySelector('textarea') : document.querySelector('textarea');
            if (!ta) return { error: 'no textarea' };

            const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
            setter.call(ta, val);
            ta.dispatchEvent(new Event('input', { bubbles: true }));
            ta.dispatchEvent(new Event('change', { bubbles: true }));
            ta.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', bubbles: true }));
            ta.blur();

            return { success: true };
        }""", { 'sel': cell_sel, 'val': new_value })
        print(f"Edit text cell [{row},{col}]:", set_res)
        await asyncio.sleep(0.4)

    # -------------------------------------------------------------
    # Helper to select option in a dropdown cell
    # -------------------------------------------------------------
    async def select_dropdown_cell(row, col, option_text):
        cell_sel = f'[data-cell="{row}-{col}"]'
        await mercor_page.evaluate("""(sel) => {
            const cell = document.querySelector(sel);
            if (!cell) return;
            cell.scrollIntoView({ block: 'center' });
            const key = Object.keys(cell).find(k => k.startsWith('__reactFiber$'));
            let f = cell[key];
            if (f && f.memoizedProps.onDoubleClick) {
                f.memoizedProps.onDoubleClick({ preventDefault: () => {}, stopPropagation: () => {} });
            }
        }""", cell_sel)
        await asyncio.sleep(0.5)

        opt_res = await mercor_page.evaluate("""(opt) => {
            const options = Array.from(document.querySelectorAll('[role="option"]'));
            const target = options.find(o => (o.innerText || '').includes(opt));
            if (target) {
                target.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true }));
                target.dispatchEvent(new MouseEvent('mousedown', { bubbles: true }));
                target.dispatchEvent(new PointerEvent('pointerup', { bubbles: true }));
                target.dispatchEvent(new MouseEvent('mouseup', { bubbles: true }));
                target.dispatchEvent(new MouseEvent('click', { bubbles: true }));
                return { selected: true, text: target.innerText.trim() };
            }
            return { selected: false, count: options.length };
        }""", option_text)
        print(f"Select dropdown cell [{row},{col}] -> '{option_text}':", opt_res)
        await asyncio.sleep(0.4)

    # Expand rubric accordion if closed
    await mercor_page.evaluate("""() => {
        const cell = document.querySelector('[data-cell="1-1"]');
        if (cell) return;
        const els = Array.from(document.querySelectorAll('*')).filter(el => (el.innerText || '').trim() === 'RUBRIC' && el.children.length === 0);
        if (els.length > 0) els[0].parentElement.click();
    }""")
    await asyncio.sleep(1.0)

    # 1. Update Rubric 2 (Row 1):
    # Criteria: Are declared outputs that exist on disk with the wrong filesystem type recorded in a distinct category rather than being lumped together with absent outputs?
    # Dim: 5 · Instruction Following & Scope Discipline
    # Source: EXPLICIT_PROMPT
    print("--- Updating Rubric 2 ---")
    await edit_text_cell(1, 1, "Are declared outputs that exist on disk with the wrong filesystem type recorded in a distinct category rather than being lumped together with absent outputs?")
    await select_dropdown_cell(1, 2, "Instruction Following")
    await select_dropdown_cell(1, 3, "EXPLICIT_PROMPT")

    # 2. Update Rubric 8 (Row 7):
    # Criteria: Does the test suite include a test verifying behavior when an output points through a symlink to a mismatched filesystem type (such as a declared file output pointing to a directory)?
    # Dim: 7 · Verification & Testing Discipline
    # Source: COMMON_ENGINEERING_KNOWLEDGE
    print("--- Updating Rubric 8 ---")
    await edit_text_cell(7, 1, "Does the test suite include a test verifying behavior when an output points through a symlink to a mismatched filesystem type (such as a declared file output pointing to a directory)?")
    await select_dropdown_cell(7, 2, "Verification & Testing Discipline")
    await select_dropdown_cell(7, 3, "COMMON_ENGINEERING_KNOWLEDGE")

    # 3. Update Rubric 15 (Row 14):
    # Criteria: Does the test suite include a test verifying that an intermediate symlink pointing to a non-existent target (a dangling intermediate symlink) is handled?
    # Dim: 7 · Verification & Testing Discipline
    # Source: COMMON_ENGINEERING_KNOWLEDGE
    print("--- Updating Rubric 15 ---")
    await edit_text_cell(14, 1, "Does the test suite include a test verifying that an intermediate symlink pointing to a non-existent target (a dangling intermediate symlink) is handled?")
    await select_dropdown_cell(14, 2, "Verification & Testing Discipline")
    await select_dropdown_cell(14, 3, "COMMON_ENGINEERING_KNOWLEDGE")

    # 4. Update Dropdown Answers for Side B:
    # Rubric 2 answer B -> YES
    # Rubric 8 answer B -> NO
    print("--- Updating Side B Rubric Answers ---")
    await mercor_page.evaluate("""() => {
        const comboboxes = Array.from(document.querySelectorAll('[role="combobox"]'));
        
        // Find Rubric 2 answer (B)
        const cbR2 = comboboxes.find(b => {
            const p = b.closest('div')?.parentElement?.parentElement?.innerText || '';
            return p.includes('Rubric 2 · answer (B)');
        });
        if (cbR2 && cbR2.innerText.trim() !== 'YES') {
            cbR2.click();
        }
    }""")
    await asyncio.sleep(0.5)
    await mercor_page.evaluate("""() => {
        const options = Array.from(document.querySelectorAll('[role="option"]'));
        const yesOpt = options.find(o => (o.innerText || '').trim() === 'YES');
        if (yesOpt) {
            yesOpt.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true }));
            yesOpt.dispatchEvent(new MouseEvent('click', { bubbles: true }));
        }
    }""")
    await asyncio.sleep(0.5)

    await mercor_page.evaluate("""() => {
        const comboboxes = Array.from(document.querySelectorAll('[role="combobox"]'));
        
        // Find Rubric 8 answer (B)
        const cbR8 = comboboxes.find(b => {
            const p = b.closest('div')?.parentElement?.parentElement?.innerText || '';
            return p.includes('Rubric 8 · answer (B)');
        });
        if (cbR8 && cbR8.innerText.trim() !== 'NO') {
            cbR8.click();
        }
    }""")
    await asyncio.sleep(0.5)
    await mercor_page.evaluate("""() => {
        const options = Array.from(document.querySelectorAll('[role="option"]'));
        const noOpt = options.find(o => (o.innerText || '').trim() === 'NO');
        if (noOpt) {
            noOpt.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true }));
            noOpt.dispatchEvent(new MouseEvent('click', { bubbles: true }));
        }
    }""")
    await asyncio.sleep(0.5)

    # 5. Update Textareas (all reasons and citations):
    print("--- Updating Textareas ---")
    new_r2_reason_b = "Yes. Model B introduces invalid_output_path in ExecLogEntry.Output and distinguishes outputs that exist on disk with the wrong filesystem type from genuinely absent outputs (missing_path). Both categories are handled distinctly in getOutputType and in the test suite reconstruction."
    new_r6_reason_b = "Model B added replacement test cases in SpawnLogContextTestBase.java, specifically introducing testFileOutput_wrongType to cover the directory-as-file mismatch scenario previously handled by testDirectoryOutput. The execution logs from its test run confirm that testFileOutput_wrongType[WITHOUT_BYTES] and testFileOutput_wrongType[WITH_BYTES] were compiled, executed, and passed."
    new_r8_reason_b = "No. While Model B introduced testFileOutput_wrongType for a direct directory-as-file mismatch, it did not add tests exercising intermediate symlinks pointing to mismatched filesystem types (such as a declared file output backed by a symlink to a directory)."
    new_r10_reason_b = "The execution log of Model B records //src/test/java/com/google/devtools/build/lib/exec:ExecTests PASSED in 8.7s under call_129_c and records 37 errors='0' under call_141_c, corroborating the counts its summary states."
    new_r15_reason_b = "No. Model B added tests for standard symlink and wrong-type outputs, but did not include a test covering a dangling intermediate symlink (where a declared file or directory output points to a broken symlink)."

    ta_updates = await mercor_page.evaluate("""({ r2, r6, r8, r10, r15 }) => {
        const tas = Array.from(document.querySelectorAll('textarea'));
        const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
        const modified = [];

        for (let i = 0; i < tas.length; i++) {
            const ta = tas[i];
            let val = ta.value;

            // TA #5: Dim 6 Reason A
            if (val.includes('A spent 107 terminal calls') && (val.includes('230, 233') || val.includes('323-entry'))) {
                val = val.replace('at entries 68, 71, 230, 233, 317 and 320', 'across multiple verification calls')
                         .replace('across a 323-entry log', 'across its rollout log');
                setter.call(ta, val);
                ta.dispatchEvent(new Event('input', { bubbles: true }));
                ta.dispatchEvent(new Event('change', { bubbles: true }));
                modified.push('ta_dim_6_a');
            }

            // TA #6: Dim 7 Reason A
            if (val.includes('A authored the broader suite') && val.includes('323 entries')) {
                val = val.replace('in its 323 entries', 'in its recorded trajectory');
                setter.call(ta, val);
                ta.dispatchEvent(new Event('input', { bubbles: true }));
                ta.dispatchEvent(new Event('change', { bubbles: true }));
                modified.push('ta_dim_7_a');
            }

            // TA #7: Dim 8 Reason A
            if (val.includes("A's 323-entry log is 108 step markers")) {
                val = val.replace("A's 323-entry log is 108 step markers, 107 tool calls", "A's trajectory consists of 107 tool calls");
                setter.call(ta, val);
                ta.dispatchEvent(new Event('input', { bubbles: true }));
                ta.dispatchEvent(new Event('change', { bubbles: true }));
                modified.push('ta_dim_8_a');
            }

            // TA #8: Dim 9 Reason A
            if (val.includes("A's 946-character summary") && val.includes('323 entries')) {
                val = val.replace('in its 323 entries', 'in its recorded trajectory');
                setter.call(ta, val);
                ta.dispatchEvent(new Event('input', { bubbles: true }));
                ta.dispatchEvent(new Event('change', { bubbles: true }));
                modified.push('ta_dim_9_a');
            }

            // TA #18: Rubric 2 Reason B
            if (i === 19 || val.includes('Model B introduces invalid_output_path') || val.includes('ExceLogEntry.Output')) {
                setter.call(ta, r2);
                ta.dispatchEvent(new Event('input', { bubbles: true }));
                ta.dispatchEvent(new Event('change', { bubbles: true }));
                modified.push('ta_r2_b');
            }

            // TA #22: Rubric 6 Reason B
            if (i === 23 || val.includes('SpawnLogContextTestBae.java') || val.includes('testFileOutput_wrongType')) {
                setter.call(ta, r6);
                ta.dispatchEvent(new Event('input', { bubbles: true }));
                ta.dispatchEvent(new Event('change', { bubbles: true }));
                modified.push('ta_r6_b');
            }

            // TA #24: Rubric 8 Reason B
            if (i === 25 || val.includes("B's proto work is confined to the two additions")) {
                setter.call(ta, r8);
                ta.dispatchEvent(new Event('input', { bubbles: true }));
                ta.dispatchEvent(new Event('change', { bubbles: true }));
                modified.push('ta_r8_b');
            }

            // TA #26: Rubric 10 Reason B
            if (i === 27 || val.includes('Entry 194 of B')) {
                setter.call(ta, r10);
                ta.dispatchEvent(new Event('input', { bubbles: true }));
                ta.dispatchEvent(new Event('change', { bubbles: true }));
                modified.push('ta_r10_b');
            }

            // TA #31: Rubric 15 Reason B
            if (i === 32 || val.includes('No, same gap. B rewrote the output classification')) {
                setter.call(ta, r15);
                ta.dispatchEvent(new Event('input', { bubbles: true }));
                ta.dispatchEvent(new Event('change', { bubbles: true }));
                modified.push('ta_r15_b');
            }

            // TA #32: Comparative Rationale
            if (val.includes('Both rollouts restructure the output loop') && (val.includes('entries 194 and 214') || val.includes('323 entries'))) {
                val = val.replace('corroborated at entries 194 and 214 of its own log', 'corroborated under call_129_c and call_141_c of its own log')
                         .replace('anywhere in its 323 entries', 'anywhere in its recorded trajectory');
                setter.call(ta, val);
                ta.dispatchEvent(new Event('input', { bubbles: true }));
                ta.dispatchEvent(new Event('change', { bubbles: true }));
                modified.push('ta_comparative');
            }
        }

        return modified;
    }""", { 'r2': new_r2_reason_b, 'r6': new_r6_reason_b, 'r8': new_r8_reason_b, 'r10': new_r10_reason_b, 'r15': new_r15_reason_b })
    print("Textareas modified:", ta_updates)
    await asyncio.sleep(1.0)

    # 6. Save Changes
    print("--- Saving Changes ---")
    save_res = await mercor_page.evaluate("""() => {
        const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.trim() === 'Save Changes');
        if (btn) {
            btn.click();
            return { clicked: true, disabled: btn.disabled };
        }
        return { clicked: false };
    }""")
    print("Save Changes result:", save_res)
    await asyncio.sleep(3.0)

    # 7. Trigger AutoQC
    print("--- Triggering AutoQC ---")
    run_qc = await mercor_page.evaluate("""() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const target = btns.find(b => b.innerText.includes('Run AutoQC') || b.innerText.includes('Rerun 4 failing'));
        if (target) {
            target.click();
            return { clicked: true, text: target.innerText };
        }
        return { clicked: false, allBtns: btns.map(b => b.innerText.trim()).filter(t => t.includes('AutoQC') || t.includes('Rerun')) };
    }""")
    print("AutoQC trigger:", run_qc)

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
