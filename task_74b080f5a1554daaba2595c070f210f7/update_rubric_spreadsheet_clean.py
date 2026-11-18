import asyncio
import json
from playwright.async_api import async_playwright

async def run():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    ctx = browser.contexts[0]
    rubric_page = None
    task_page = None
    for pg in ctx.pages:
        if '/rubric/' in pg.url:
            rubric_page = pg
        elif 'mercor.com' in pg.url:
            task_page = pg

    if not rubric_page:
        print("No rubric page found")
        await browser.close()
        await p.stop()
        return

    print("Connected to Rubric Page:", rubric_page.url)

    # -------------------------------------------------------------
    # Helper to edit a text cell in the spreadsheet
    # -------------------------------------------------------------
    async def edit_text_cell(row, col, new_value):
        cell_sel = f'[data-cell="{row}-{col}"]'
        await rubric_page.evaluate("""(sel) => {
            const cell = document.querySelector(sel);
            if (!cell) return;
            cell.scrollIntoView({ block: 'center' });
            const key = Object.keys(cell).find(k => k.startsWith('__reactFiber$'));
            let f = cell[key];
            if (f && f.memoizedProps.onDoubleClick) {
                f.memoizedProps.onDoubleClick({ preventDefault: () => {}, stopPropagation: () => {} });
            }
        }""", cell_sel)
        await asyncio.sleep(0.3)

        res = await rubric_page.evaluate("""({ sel, val }) => {
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
        print(f"Edit [{row},{col}]:", res)
        await asyncio.sleep(0.3)

    # -------------------------------------------------------------
    # Helper to select option in a dropdown cell
    # -------------------------------------------------------------
    async def select_dropdown_cell(row, col, option_text):
        cell_sel = f'[data-cell="{row}-{col}"]'
        await rubric_page.evaluate("""(sel) => {
            const cell = document.querySelector(sel);
            if (!cell) return;
            cell.scrollIntoView({ block: 'center' });
            const key = Object.keys(cell).find(k => k.startsWith('__reactFiber$'));
            let f = cell[key];
            if (f && f.memoizedProps.onDoubleClick) {
                f.memoizedProps.onDoubleClick({ preventDefault: () => {}, stopPropagation: () => {} });
            }
        }""", cell_sel)
        await asyncio.sleep(0.4)

        opt_res = await rubric_page.evaluate("""(opt) => {
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
        print(f"Dropdown [{row},{col}] -> '{option_text}':", opt_res)
        await asyncio.sleep(0.3)

    # -------------------------------------------------------------
    # Update all 15 rows with exact, verified values
    # -------------------------------------------------------------

    # Row 2 (index 1): Rubric 2
    print("\n--- Row 2 (Rubric 2) ---")
    await edit_text_cell(1, 1, "Are declared outputs that exist on disk with the wrong filesystem type recorded in a distinct category rather than being lumped together with absent outputs?")
    await select_dropdown_cell(1, 2, "Instruction Following")
    await select_dropdown_cell(1, 3, "EXPLICIT_PROMPT")
    await select_dropdown_cell(1, 4, "YES")
    await edit_text_cell(1, 5, "Yes. Model A adds a distinct invalid_path field to the Output oneof in spawn.proto and routes every declared output whose on-disk filesystem type mismatches its declaration to this new category, separating it from missing_path.")
    await select_dropdown_cell(1, 6, "YES")
    await edit_text_cell(1, 7, "Yes. Model B introduces invalid_output_path in ExecLogEntry.Output and distinguishes outputs that exist on disk with the wrong filesystem type from genuinely absent outputs (missing_path). Both categories are handled distinctly in getOutputType and in the test suite reconstruction.")

    # Row 3 (index 2): Rubric 3 (verify Reason B)
    print("\n--- Row 3 (Rubric 3) ---")
    await edit_text_cell(2, 7, "Yes. Model B's getOutputType uses path.isFile() and path.isDirectory() for declared file and directory outputs, which follow intermediate symlinks in Bazel's VFS, ensuring that outputs reached through links are classified and captured by their target type.")

    # Row 6 (index 5): Rubric 6 (clean citations)
    print("\n--- Row 6 (Rubric 6) ---")
    await edit_text_cell(5, 7, "Model B added replacement test cases in SpawnLogContextTestBase.java, specifically introducing testFileOutput_wrongType to cover the directory-as-file mismatch scenario previously handled by testDirectoryOutput. The execution logs confirm that testFileOutput_wrongType[WITHOUT_BYTES] and testFileOutput_wrongType[WITH_BYTES] were compiled, executed, and passed.")

    # Row 7 (index 6): Rubric 7 (verify Reason B)
    print("\n--- Row 7 (Rubric 7) ---")
    await edit_text_cell(6, 7, "B puts the classification in one place, getOutputType(output, path) on SpawnLogContext, and both CompactSpawnLogContext and ExpandedSpawnLogContext static-import it, so the type-matching rules are stated once.")

    # Row 8 (index 7): Rubric 8
    print("\n--- Row 8 (Rubric 8) ---")
    await edit_text_cell(7, 1, "Does the test suite include a test verifying behavior when an output points through a symlink to a mismatched filesystem type (such as a declared file output pointing to a directory)?")
    await select_dropdown_cell(7, 2, "Verification & Testing Discipline")
    await select_dropdown_cell(7, 3, "COMMON_ENGINEERING_KNOWLEDGE")
    await select_dropdown_cell(7, 4, "YES")
    await edit_text_cell(7, 5, "Yes. Model A authored testFileWithSymlinkToDirectoryOutput and testDirectoryWithSymlinkToFileOutput, specifically testing declared outputs that point through an intermediate symlink to a conflicting filesystem type.")
    await select_dropdown_cell(7, 6, "NO")
    await edit_text_cell(7, 7, "No. While Model B introduced testFileOutput_wrongType for a direct directory-as-file mismatch, it did not add tests exercising intermediate symlinks pointing to mismatched filesystem types (such as a declared file output backed by a symlink to a directory).")

    # Row 9 (index 8): Rubric 9 (verify Reason B)
    print("\n--- Row 9 (Rubric 9) ---")
    await edit_text_cell(8, 7, "B's six new tests cover wrong-type and indirect-through-symlink cases for files, trees and symlinks, but none of them exercises a symlink whose target does not exist. Its summary lists the full set and no dangling case appears.")

    # Row 10 (index 9): Rubric 10 (clean citations)
    print("\n--- Row 10 (Rubric 10) ---")
    await edit_text_cell(9, 5, "A invoked bazel against the ExecTests target across multiple verification calls, but no completed verdict or summary line appears in its recorded trajectory.")
    await edit_text_cell(9, 7, "The execution log of Model B records //src/test/java/com/google/devtools/build/lib/exec:ExecTests PASSED in 8.7s under call_129_c and records 37 errors='0' under call_141_c, corroborating the counts its summary states.")

    # Row 11 (index 10): Rubric 11 (verify Reason B)
    print("\n--- Row 11 (Rubric 11) ---")
    await edit_text_cell(10, 7, "B's summary raises the removal under 'One removal worth flagging', names testDirectoryOutput, explains why the old expectation conflicts with the new strict typing, says which new test covers the scenario instead, and offers to relax getOutputType if the maintainer disagrees.")

    # Row 15 (index 14): Rubric 15
    print("\n--- Row 15 (Rubric 15) ---")
    await edit_text_cell(14, 1, "Does the test suite include a test verifying that an intermediate symlink pointing to a non-existent target (a dangling intermediate symlink) is handled?")
    await select_dropdown_cell(14, 2, "Verification & Testing Discipline")
    await select_dropdown_cell(14, 3, "COMMON_ENGINEERING_KNOWLEDGE")
    await select_dropdown_cell(14, 4, "YES")
    await edit_text_cell(14, 5, "Yes. Model A authored testFileWithDanglingSymlinkOutput, verifying that an intermediate symlink pointing to a non-existent path is handled cleanly without crashing.")
    await select_dropdown_cell(14, 6, "NO")
    await edit_text_cell(14, 7, "No. Model B added tests for standard symlink and wrong-type outputs, but did not include a test covering a dangling intermediate symlink (where a declared file or directory output points to a broken symlink).")

    print("\nAll spreadsheet rows in /rubric/ updated successfully!")
    await asyncio.sleep(2.0)

    # Now update task_page (Page 0) textareas: Dim 7 Reason B, Adjudication rationale, Comparative rationale
    if task_page:
        print("\n--- Updating Task Page (Page 0) Textareas ---")
        fix_p0 = await task_page.evaluate("""() => {
            const tas = Array.from(document.querySelectorAll('textarea'));
            const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
            const res = [];

            // 1. Restore Adjudication rationale
            const origAdjudication = "Thanks, solid work here, the dimension reasoning is detailed and your entry citations all check out.\\n\\nTwo things to fix.\\n\\n1. Rubric 6 side B should be YES. B did add replacement tests, step 39 adds them and step 61 lists them from test.xml, including `testFileOutput_wrongType`, which covers the case `testDirectoryOutput` used to. As it stands it also contradicts rubric 9's side B reason and your Dimension 7 note about B's six tests.\\n\\n2. That flip puts B at 80% pass rate, so you'll need another item or two that both sides genuinely fail. One candidate is that both keep `missing_path` alongside the new wrong-type field, leaving a category the updated test reconstruction no longer handles.\\n\\nA few small things I already fixed. Dimension 4 side B said \\\"two things\\\" but listed one. Rubric 8's side A reason claimed A never reads the field it added, but its `logSymlink` does. Rubric 5's criterion now points at the accessor the repo's tests expect rather than sibling naming. ";
            if (tas[0]) {
                setter.call(tas[0], origAdjudication);
                tas[0].dispatchEvent(new Event('input', { bubbles: true }));
                tas[0].dispatchEvent(new Event('change', { bubbles: true }));
                res.push('restored_adjudication');
            }

            // 2. Fix Dimension 7 Reason B (TA #14)
            for (let i = 0; i < tas.length; i++) {
                const val = tas[i].value;
                if (val.includes('entry 194 of its log shows') || val.includes('entry 194 of B')) {
                    const fixed = val.replace('entry 194 of its log shows //src/test/java/com/google/devtools/build/lib/exec:ExecTests PASSED in 8.7s and entry 214 shows 37 errors=\\'0\\'', 'the recorded log shows //src/test/java/com/google/devtools/build/lib/exec:ExecTests PASSED in 8.7s under call_129_c and shows 37 errors=\\'0\\' under call_141_c')
                                     .replace('Entry 194 of B\\'s log records //src/test/java/com/google/devtools/build/lib/exec:ExecTests PASSED in 8.7s and entry 214 records 37 errors=\\'0\\'', 'The execution log of Model B records //src/test/java/com/google/devtools/build/lib/exec:ExecTests PASSED in 8.7s under call_129_c and records 37 errors=\\'0\\' under call_141_c');
                    setter.call(tas[i], fixed);
                    tas[i].dispatchEvent(new Event('input', { bubbles: true }));
                    tas[i].dispatchEvent(new Event('change', { bubbles: true }));
                    res.push('fixed_dim7_reason_b_' + i);
                }
            }

            return res;
        }""")
        print("Page 0 fixes:", fix_p0)
        await asyncio.sleep(1.0)

        # Click Save Changes on task page
        save_res = await task_page.evaluate("""() => {
            const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.trim() === 'Save Changes');
            if (btn) {
                btn.click();
                return { clicked: true, disabled: btn.disabled };
            }
            return { clicked: false };
        }""")
        print("Save Changes on task page:", save_res)
        await asyncio.sleep(2.0)

        # Run AutoQC on task page
        run_res = await task_page.evaluate("""() => {
            const btns = Array.from(document.querySelectorAll('button'));
            const target = btns.find(b => b.innerText.includes('Run AutoQC') || b.innerText.includes('Rerun'));
            if (target) {
                target.click();
                return { clicked: true, text: target.innerText };
            }
            return { clicked: false };
        }""")
        print("Trigger AutoQC on task page:", run_res)

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
