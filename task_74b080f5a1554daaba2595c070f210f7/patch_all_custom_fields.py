import asyncio
import json
from playwright.async_api import async_playwright

CUSTOM_FIELD_UPDATES = {
    "field_ta_rubric_02_answer_a": "YES",
    "field_ta_rubric_02_reason_a": "Yes. Model A's patch in artifact_files_a/0.patch retains case MISSING_PATH and adds case INVALID_PATH. In both CompactSpawnLogContext and ExpandedSpawnLogContext, its output loop uses setMissingPath for absent outputs and setInvalidPath for wrong-type outputs, recording them in a distinct category.",
    
    "field_ta_rubric_03_answer_b": "YES",
    "field_ta_rubric_03_reason_b": "Yes. Model B's getOutputType uses path.isFile() and path.isDirectory() for declared file and directory outputs, which follow intermediate symlinks in Bazel's VFS, ensuring that outputs reached through links are classified and captured by their target type.",
    
    "field_ta_rubric_07_answer_b": "YES",
    "field_ta_rubric_07_reason_b": "Yes. Model B factors the output classification into one shared helper, getOutputType(output, path) on SpawnLogContext, and both CompactSpawnLogContext and ExpandedSpawnLogContext static-import it, avoiding duplicate classification logic across the two classes.",
    
    "field_ta_rubric_08_answer_a": "YES",
    "field_ta_rubric_08_reason_a": "Yes. Model A authored testFileWithSymlinkToDirectoryOutput and testDirectoryWithSymlinkToFileOutput in its patch, verifying behavior when a declared output points through an intermediate symlink to a conflicting filesystem type.",
    
    "field_ta_rubric_09_answer_b": "NO",
    "field_ta_rubric_09_reason_b": "No. Model B added tests covering symlink and wrong-type outputs, but did not include a test covering a dangling symlink output where the declared symlink's target does not exist on disk.",
    
    "field_ta_rubric_10_answer_a": "YES",
    "field_ta_rubric_10_reason_a": "Yes. The recorded transcript in transcript_file_a/0.json includes multiple completed ExecTests PASSED test run results following Model A's verification executions.",
    
    "field_ta_rubric_11_answer_b": "YES",
    "field_ta_rubric_11_reason_b": "Yes. In its final summary under 'One removal worth flagging', Model B explicitly discloses that it removed testDirectoryOutput, explains why the old assertion conflicts with strict typing, and notes the replacement test case covering the scenario.",
    
    "field_ta_rubric_15_answer_a": "YES",
    "field_ta_rubric_15_reason_a": "Yes. Model A authored testFileWithDanglingSymlinkOutput in its patch, verifying that a declared output pointing through an intermediate symlink to a non-existent target (a dangling intermediate symlink) is properly handled.",
    
    "field_ta_rubric_15_answer_b": "NO",
    "field_ta_rubric_15_reason_b": "No. Model B added tests for standard symlinks and wrong-type outputs, but did not include a test verifying that an intermediate symlink pointing to a non-existent target (a dangling intermediate symlink) is handled."
}

async def run():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = browser.contexts[0].pages[0]

    # 1. Send PATCH request
    print("1. Sending PATCH request with updated custom_fields...")
    patch_res = await page.evaluate("""async (updates) => {
        const token = await window.Clerk.session.getToken();
        const campaignId = localStorage.getItem('x-campaign-id') || 'camp_75099d23386f4394ab7596a5ea538da8';
        const companyId = localStorage.getItem('x-company-id') || '';
        const accountId = localStorage.getItem('x-account-id') || '';
        const headers = {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json',
            'x-campaign-id': campaignId,
            'x-company-id': companyId,
            'x-account-id': accountId
        };
        const r = await fetch('https://api.studio.mercor.com/tasks/task_74b080f5a1554daaba2595c070f210f7', {
            method: 'PATCH',
            headers,
            body: JSON.stringify({ custom_fields: updates })
        });
        const d = await r.json();
        return { status: r.status, ok: r.ok, updated_at: d.updated_at };
    }""", CUSTOM_FIELD_UPDATES)
    print("PATCH result:", patch_res)
    await asyncio.sleep(1.0)

    # 2. Reload page
    print("2. Reloading page...")
    await page.reload()
    await asyncio.sleep(4.0)

    # 3. Open Deliverable AutoQC
    print("3. Opening Deliverable AutoQC...")
    await page.evaluate("""() => {
        const els = Array.from(document.querySelectorAll('*')).filter(el => {
            return (el.innerText || '').trim() === 'DELIVERABLE AUTOQC' && el.children.length === 0;
        });
        if (els.length > 0) {
            const header = els[0].closest('button') || els[0].parentElement;
            header.scrollIntoView({ block: 'center' });
            header.click();
        }
    }""")
    await asyncio.sleep(1.5)

    # 4. Click Run AutoQC
    print("4. Triggering Run AutoQC...")
    click_res = await page.evaluate("""() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const b = btns.find(b => (b.innerText || '').trim() === 'Run AutoQC' || b.innerText.includes('Rerun'));
        if (b) {
            b.scrollIntoView({ block: 'center' });
            b.click();
            return { clicked: true, text: b.innerText };
        }
        return { clicked: false, all: btns.map(x => x.innerText.trim()).filter(t => t.includes('AutoQC')) };
    }""")
    print("Run AutoQC click:", click_res)

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
