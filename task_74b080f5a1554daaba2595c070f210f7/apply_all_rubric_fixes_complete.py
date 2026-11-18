import asyncio
from playwright.async_api import async_playwright

UPDATES = [
    {
        "cell": "1-5",
        "name": "R2 Reason A",
        "text": "Yes. Model A's patch in artifact_files_a/0.patch retains case MISSING_PATH and adds case INVALID_PATH. In both CompactSpawnLogContext and ExpandedSpawnLogContext, its output loop uses setMissingPath for absent outputs and setInvalidPath for wrong-type outputs, recording them in a distinct category."
    },
    {
        "cell": "2-7",
        "name": "R3 Reason B",
        "text": "Yes. Model B's getOutputType uses path.isFile() and path.isDirectory() for declared file and directory outputs, which follow intermediate symlinks in Bazel's VFS, ensuring that outputs reached through links are classified and captured by their target type."
    },
    {
        "cell": "6-7",
        "name": "R7 Reason B",
        "text": "Yes. Model B factors the output classification into one shared helper, getOutputType(output, path) on SpawnLogContext, and both CompactSpawnLogContext and ExpandedSpawnLogContext static-import it, avoiding duplicate classification logic across the two classes."
    },
    {
        "cell": "7-5",
        "name": "R8 Reason A",
        "text": "Yes. Model A authored testFileWithSymlinkToDirectoryOutput and testDirectoryWithSymlinkToFileOutput in its patch, verifying behavior when a declared output points through an intermediate symlink to a conflicting filesystem type."
    },
    {
        "cell": "9-5",
        "name": "R10 Reason A",
        "text": "Yes. The recorded transcript in transcript_file_a/0.json includes multiple completed ExecTests PASSED test run results following Model A's verification executions."
    },
    {
        "cell": "10-7",
        "name": "R11 Reason B",
        "text": "Yes. In its final summary under 'One removal worth flagging', Model B explicitly discloses that it removed testDirectoryOutput, explains why the old assertion conflicts with strict typing, and notes the replacement test case covering the scenario."
    }
]

async def run():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    ctx = browser.contexts[0]
    rubric_page = None
    for pg in ctx.pages:
        if '/rubric/' in pg.url:
            rubric_page = pg
            break

    if not rubric_page:
        print("No rubric page found!")
        await browser.close()
        await p.stop()
        return

    print("Connected to Rubric Page:", rubric_page.url)

    # 1. Update text cells
    for item in UPDATES:
        cell_sel = f'[data-cell="{item["cell"]}"]'
        val = item["text"]
        name = item["name"]

        # Phase 1: Enter edit mode
        p1 = await rubric_page.evaluate("""(sel) => {
            const cell = document.querySelector(sel);
            if (!cell) return { error: 'cell not found: ' + sel };
            cell.scrollIntoView({ block: 'center' });

            const key = Object.keys(cell).find(k => k.startsWith('__reactFiber$'));
            let f = cell[key];
            if (f && f.memoizedProps.onDoubleClick) {
                f.memoizedProps.onDoubleClick({ preventDefault: () => {}, stopPropagation: () => {} });
                return { dblclicked: true };
            }
            return { error: 'no onDoubleClick' };
        }""", cell_sel)
        
        await asyncio.sleep(0.4)

        # Phase 2: Set value and commit
        p2 = await rubric_page.evaluate("""({ sel, val }) => {
            const cell = document.querySelector(sel);
            const ta = cell ? cell.querySelector('textarea') : document.querySelector('textarea');
            if (!ta) return { error: 'no textarea mounted' };

            const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
            setter.call(ta, val);
            ta.dispatchEvent(new Event('input', { bubbles: true }));
            ta.dispatchEvent(new Event('change', { bubbles: true }));
            ta.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', bubbles: true }));
            ta.blur();

            return { success: true };
        }""", { 'sel': cell_sel, 'val': val })

        await asyncio.sleep(0.4)

        # Phase 3: Verify
        actual = await rubric_page.evaluate("""(sel) => {
            return document.querySelector(sel)?.innerText?.trim();
        }""", cell_sel)

        if actual == val:
            print(f"[OK] {name} ({item['cell']}) updated perfectly!")
        else:
            print(f"[WARN] {name} ({item['cell']}) mismatch: expected {len(val)} chars, got {len(actual) if actual else 0}")
            print(f"  actual: {actual}")

    # 2. Verify all dropdown answers
    dropdown_checks = [
        ("1-4", "R2 Ans A", "YES"),
        ("7-4", "R8 Ans A", "YES"),
        ("9-4", "R10 Ans A", "YES"),
        ("1-6", "R2 Ans B", "YES"),
        ("7-6", "R8 Ans B", "NO"),
        ("9-6", "R10 Ans B", "YES"),
    ]
    print("\n--- Verifying Dropdown Answers ---")
    for cell_id, name, expected in dropdown_checks:
        actual = await rubric_page.evaluate(f"""() => {{
            return document.querySelector('[data-cell="{cell_id}"]')?.innerText?.trim();
        }}""")
        if actual == expected:
            print(f"[OK] {name} ({cell_id}): {actual}")
        else:
            print(f"[MISMATCH] {name} ({cell_id}): expected {expected}, got {actual}")
            # Fix it if needed
            print(f"  Fixing {name}...")
            await rubric_page.evaluate(f"""() => {{
                const cell = document.querySelector('[data-cell="{cell_id}"]');
                const key = Object.keys(cell).find(k => k.startsWith('__reactFiber$'));
                let f = cell[key];
                if (f && f.memoizedProps.onDoubleClick) {{
                    f.memoizedProps.onDoubleClick({{ preventDefault: () => {{}}, stopPropagation: () => {{}} }});
                }}
            }}""")
            await asyncio.sleep(0.5)
            await rubric_page.evaluate(f"""() => {{
                const options = Array.from(document.querySelectorAll('[role="option"], div, span')).filter(el => {{
                    const t = (el.innerText || '').trim();
                    return t === '{expected}' && el.children.length === 0;
                }});
                if (options.length > 0) {{
                    const target = options[options.length - 1];
                    target.dispatchEvent(new PointerEvent('pointerdown', {{ bubbles: true }}));
                    target.dispatchEvent(new MouseEvent('mousedown', {{ bubbles: true }}));
                    target.dispatchEvent(new PointerEvent('pointerup', {{ bubbles: true }}));
                    target.dispatchEvent(new MouseEvent('mouseup', {{ bubbles: true }}));
                    target.dispatchEvent(new MouseEvent('click', {{ bubbles: true }}));
                }}
            }}""")
            await asyncio.sleep(0.5)
            new_actual = await rubric_page.evaluate(f"""() => {{
                return document.querySelector('[data-cell="{cell_id}"]')?.innerText?.trim();
            }}""")
            print(f"  Now {name} ({cell_id}): {new_actual}")

    # Wait for "All changes saved"
    print("\nWaiting for autosave...")
    for _ in range(10):
        saved = await rubric_page.evaluate("""() => {
            return document.body.innerText.includes('All changes saved');
        }""")
        if saved:
            print("Status: All changes saved!")
            break
        await asyncio.sleep(1.0)

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
