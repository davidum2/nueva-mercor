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

    for item in UPDATES:
        cell_id = item["cell"]
        name = item["name"]
        val = item["text"]

        res = await rubric_page.evaluate("""({ cellId, val }) => {
            const cell = document.querySelector(`[data-cell="${cellId}"]`);
            if (!cell) return { error: 'cell not found: ' + cellId };
            cell.scrollIntoView({ block: 'center' });

            const key = Object.keys(cell).find(k => k.startsWith('__reactFiber$'));
            let f = cell[key];
            if (f && f.memoizedProps.onDoubleClick) {
                f.memoizedProps.onDoubleClick({ preventDefault: () => {}, stopPropagation: () => {} });
            }

            const ta = cell.querySelector('textarea') || document.querySelector('textarea');
            if (!ta) return { error: 'no textarea for ' + cellId };

            const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
            setter.call(ta, val);
            ta.dispatchEvent(new Event('input', { bubbles: true }));
            ta.dispatchEvent(new Event('change', { bubbles: true }));
            ta.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', bubbles: true }));
            ta.blur();

            return { success: true };
        }""", { "cellId": cell_id, "val": val })

        print(f"Updated {name} ({cell_id}): {res}")
        await asyncio.sleep(0.8)

        # Verify
        actual = await rubric_page.evaluate("""(cellId) => {
            return document.querySelector(`[data-cell="${cellId}"]`)?.innerText?.trim();
        }""", cell_id)
        if actual == val:
            print(f"  [OK] verified exact match")
        else:
            print(f"  [MISMATCH] expected len {len(val)}, got len {len(actual) if actual else 0}")
            print(f"    got: {actual[:60]}...")

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
