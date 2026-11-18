import asyncio
import json
import sys
import time
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

# Verifiers to DELETE
VER_TO_DELETE = [
    'ver_20f59b7003694f739f4287274dcb6299', # finally-close
    'ver_4af2b63c2c864e39888d96d5eee36984'  # process-command
]

# 10 Perfect Verifiers definitions
VERIFIERS_CONFIG = [
    {
        'id': 'ver_81cf796b00b7499d9094585a89a98330',
        'index': 0,
        'criteria': "Does the sample implement the required 'deidentify_cloud_storage' function with exactly 8 parameters matching downstream test callers?",
        'ans_a': "YES",
        'ans_b': "NO",
        'reason_a': "Model A implements deidentify_cloud_storage with exactly the 8 required parameters matching downstream test expectations (patch_a.diff:L60-68).",
        'reason_b': "Model B defines deidentify_cloud_storage with 9 parameters on patch_b.diff:L60-69, adding an unrequested parameter that breaks downstream invocation in PHP 8+.",
        'source': "REPO_CODE_OR_TESTS",
        'dim': "2 · Functional Correctness & Code Architecture"
    },
    {
        'id': 'ver_7dda937c36f24292bc06be412fbbd729',
        'index': 1,
        'criteria': "Does the sample resolve template names using DlpServiceBaseClient::projectDeidentifyTemplateName rather than passing unvalidated raw strings?",
        'ans_a': "NO",
        'ans_b': "NO",
        'reason_a': "Model A assigns the raw template name strings directly into setDeidentifyTemplateName without resolving canonical resource names via DlpServiceBaseClient::projectDeidentifyTemplateName (patch_a.diff:L101-103).",
        'reason_b': "Model B directly passes the raw template name string to setDeidentifyTemplateName on patch_b.diff:L88 without calling DlpServiceBaseClient::projectDeidentifyTemplateName.",
        'source': "PROJECT_CONVENTIONS",
        'dim': "2 · Functional Correctness & Code Architecture"
    },
    {
        'id': 'ver_820863c5a07d4ad18925de208f1c7bea',
        'index': 2,
        'criteria': "Does the sample attach an InspectConfig object to the InspectJobConfig to specify inspect settings?",
        'ans_a': "NO",
        'ans_b': "YES",
        'reason_a': "Model A instantiates InspectJobConfig on patch_a.diff:L114 without attaching an InspectConfig object, omitting inspect configuration settings.",
        'reason_b': "Model B creates an InspectConfig instance on patch_b.diff:L93 and attaches it to the InspectJobConfig via setInspectConfig on patch_b.diff:L101.",
        'source': "PROJECT_CONVENTIONS",
        'dim': "2 · Functional Correctness & Code Architecture"
    },
    {
        'id': 'ver_0cee99eca3c34c0abc432217b4e68cb7',
        'index': 3,
        'criteria': "Does the sample include standard Google Cloud documentation region tags '[START dlp_deidentify_cloud_storage]' and '[END dlp_deidentify_cloud_storage]'?",
        'ans_a': "YES",
        'ans_b': "YES",
        'reason_a': "Model A encloses the sample implementation cleanly within '[START dlp_deidentify_cloud_storage]' and '[END dlp_deidentify_cloud_storage]' region tags (patch_a.diff:L26, L163).",
        'reason_b': "Model B includes standard region tags '[START dlp_deidentify_cloud_storage]' and '[END dlp_deidentify_cloud_storage]' on patch_b.diff:L26 and L137.",
        'source': "PROJECT_CONVENTIONS",
        'dim': "3 · Readability, Clean Code & Coding Standards"
    },
    {
        'id': 'ver_818c1b416406417182b69fd160e570bb',
        'index': 4,
        'criteria': "Does the sample provide complete PHPDoc documentation with @param tags for all function arguments?",
        'ans_a': "YES",
        'ans_b': "YES",
        'reason_a': "Model A includes a comprehensive PHPDoc docblock documenting all 8 parameters with @param string type annotations and descriptions (patch_a.diff:L47-58).",
        'reason_b': "Model B includes PHPDoc documentation with @param annotations for its parameters on patch_b.diff:L47-57.",
        'source': "COMMON_ENGINEERING_KNOWLEDGE",
        'dim': "3 · Readability, Clean Code & Coding Standards"
    },
    {
        'id': 'ver_a001845eb61f40a480d632767533805d',
        'index': 5,
        'criteria': "Does the sample implement a bounded polling loop with a maximum retry counter or timeout to prevent infinite hanging?",
        'ans_a': "NO",
        'ans_b': "NO",
        'reason_a': "Model A implements an unbounded while loop that polls continuously without a maximum retry counter or timeout guard (patch_a.diff:L133-143).",
        'reason_b': "Model B uses an unbounded while loop on patch_b.diff:L109-114 that sleeps without enforcing a maximum iteration count or timeout guard.",
        'source': "COMMON_ENGINEERING_KNOWLEDGE",
        'dim': "4 · Robustness, Error Handling & Defensiveness"
    },
    {
        'id': 'ver_409872ec9b674f5fbe60452bc077e3e3',
        'index': 6,
        'criteria': "Does the sample inspect and handle non-terminal job states (e.g. FAILED) by reporting job errors?",
        'ans_a': "YES",
        'ans_b': "YES",
        'reason_a': "Model A handles failure states defensively by evaluating a switch on $job->getState(), printing error notices and inspecting $job->getErrors() details when JobState::FAILED occurs (patch_a.diff:L145-151).",
        'reason_b': "Model B checks whether $job->getState() !== JobState::DONE on patch_b.diff:L116-122, looping through $job->getErrors() and printing error messages when the DLP job fails.",
        'source': "PROJECT_CONVENTIONS",
        'dim': "4 · Robustness, Error Handling & Defensiveness"
    },
    {
        'id': 'ver_2ed743084af8497192d38950d3c7e9bd',
        'index': 7,
        'criteria': "Is the new sample file placed in the exact directory requested ('dlp/src/deidentify_cloud_storage.php')?",
        'ans_a': "YES",
        'ans_b': "YES",
        'reason_a': "Model A creates the newly requested sample file strictly at 'dlp/src/deidentify_cloud_storage.php' as specified in the prompt instructions, without creating unauthorized auxiliary files (patch_a.diff:L1).",
        'reason_b': "Model B places the authored sample exactly at 'dlp/src/deidentify_cloud_storage.php' on patch_b.diff:L1, adhering precisely to the target directory requirement specified in the prompt.",
        'source': "EXPLICIT_PROMPT",
        'dim': "5 · Instruction Following & Scope Discipline"
    },
    {
        'id': 'ver_3505ba0870754e8a81b5b4152a42c76f',
        'index': 8,
        'criteria': "Does the sample configure the BigQuery output table without introducing an unrequested project parameter into the public function signature?",
        'ans_a': "YES",
        'ans_b': "NO",
        'reason_a': "Model A adheres strictly to the prompt scope by using the provided $callingProjectId for the BigQuery table while taking $datasetId and $tableId as requested (patch_a.diff:L66-67, L87-90).",
        'reason_b': "Model B introduces an unrequested parameter '$transformationDetailsTableProjectId' into the public API signature (patch_b.diff:L67), modifying the expected 8-argument interface.",
        'source': "REPO_CODE_OR_TESTS",
        'dim': "5 · Instruction Following & Scope Discipline"
    },
    {
        'id': 'ver_f089360caebf462592690f71aa16031a',
        'index': 9,
        'criteria': "Did the agent run a PHP syntax linter ('php -l') on the authored sample to verify zero syntax errors?",
        'ans_a': "YES",
        'ans_b': "YES",
        'reason_a': "Model A verified code integrity in Step 50 by executing 'php -l /workspace/repo/dlp/src/deidentify_cloud_storage.php', confirming 'No syntax errors detected' prior to final submission.",
        'reason_b': "Model B executed PHP syntax validation in Step 34, confirming that the written sample passed syntax linting without syntax errors before completing its trajectory.",
        'source': "ENVIRONMENT",
        'dim': "7 · Verification & Testing Rigor"
    }
]

async def apply_perfect_calibration():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    # API updates
    api_res = await page.evaluate("""async ({ taskId, toDelete, verifiers }) => {
        const token = await window.Clerk.session.getToken({ skipCache: true });
        const headers = {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json',
            'x-campaign-id': localStorage.getItem('x-campaign-id') || 'camp_75099d23386f4394ab7596a5ea538da8',
            'x-company-id': localStorage.getItem('x-company-id') || 'comp_2fa4115109d741cd94a3c409ed89e61f',
            'x-account-id': localStorage.getItem('x-account-id') || 'acct_85b680d4c5ba49a29f19c173672aebea'
        };

        // 1. DELETE unwanted verifiers
        const delResults = [];
        for (const vid of toDelete) {
            const r = await fetch(`https://api.studio.mercor.com/verifiers/${vid}`, { method: 'DELETE', headers });
            delResults.push({ id: vid, status: r.status });
        }

        // 2. PATCH the 10 verifiers
        const patchResults = [];
        for (const v of verifiers) {
            const r = await fetch(`https://api.studio.mercor.com/verifiers/${v.id}`, {
                method: 'PATCH',
                headers,
                body: JSON.stringify({
                    verifier_index: v.index,
                    verifier_values: { criteria: v.criteria },
                    verifier_custom_field_values: {
                        answer_a: v.ans_a,
                        answer_b: v.ans_b,
                        reason_a: v.reason_a,
                        reason_b: v.reason_b,
                        rubric_source: v.source,
                        mapped_dimension: v.dim
                    }
                })
            });
            patchResults.push({ id: v.id, index: v.index, status: r.status });
        }

        // 3. PATCH task custom fields
        const custom_fields = {
            field_rubric_count: "10",
            field_ta_rubric_01_mapped_dimension_a: "2 · Functional Correctness & Code Architecture",
            field_ta_rubric_01_mapped_dimension_b: "2 · Functional Correctness & Code Architecture",
            field_ta_rubric_02_mapped_dimension_a: "2 · Functional Correctness & Code Architecture",
            field_ta_rubric_02_mapped_dimension_b: "2 · Functional Correctness & Code Architecture",
            field_ta_rubric_03_mapped_dimension_a: "2 · Functional Correctness & Code Architecture",
            field_ta_rubric_03_mapped_dimension_b: "2 · Functional Correctness & Code Architecture",
            field_ta_rubric_04_mapped_dimension_a: "3 · Readability, Clean Code & Coding Standards",
            field_ta_rubric_04_mapped_dimension_b: "3 · Readability, Clean Code & Coding Standards",
            field_ta_rubric_05_mapped_dimension_a: "3 · Readability, Clean Code & Coding Standards",
            field_ta_rubric_05_mapped_dimension_b: "3 · Readability, Clean Code & Coding Standards",
            field_ta_rubric_06_mapped_dimension_a: "4 · Robustness, Error Handling & Defensiveness",
            field_ta_rubric_06_mapped_dimension_b: "4 · Robustness, Error Handling & Defensiveness",
            field_ta_rubric_07_mapped_dimension_a: "4 · Robustness, Error Handling & Defensiveness",
            field_ta_rubric_07_mapped_dimension_b: "4 · Robustness, Error Handling & Defensiveness",
            field_ta_rubric_08_mapped_dimension_a: "5 · Instruction Following & Scope Discipline",
            field_ta_rubric_08_mapped_dimension_b: "5 · Instruction Following & Scope Discipline",
            field_ta_rubric_09_mapped_dimension_a: "5 · Instruction Following & Scope Discipline",
            field_ta_rubric_09_mapped_dimension_b: "5 · Instruction Following & Scope Discipline",
            field_ta_rubric_10_mapped_dimension_a: "7 · Verification & Testing Rigor",
            field_ta_rubric_10_mapped_dimension_b: "7 · Verification & Testing Rigor",
            field_ta_rubric_11_mapped_dimension_a: null,
            field_ta_rubric_11_mapped_dimension_b: null,
            field_ta_rubric_12_mapped_dimension_a: null,
            field_ta_rubric_12_mapped_dimension_b: null,
            field_ta_rubric_13_mapped_dimension_a: null,
            field_ta_rubric_13_mapped_dimension_b: null
        };
        const taskPatch = await fetch(`https://api.studio.mercor.com/tasks/${taskId}`, {
            method: 'PATCH',
            headers,
            body: JSON.stringify({ custom_fields })
        });

        return { delResults, patchResults, taskPatchStatus: taskPatch.status };
    }""", { 'taskId': TASK_ID, 'toDelete': VER_TO_DELETE, 'verifiers': VERIFIERS_CONFIG })

    print("API Execution Results:", json.dumps(api_res, indent=2), flush=True)

    # Update Rubric count in UI combobox if present
    count_btn = page.locator('button[role="combobox"]').filter(has_text="12")
    if await count_btn.count() > 0:
        await count_btn.first.click()
        await asyncio.sleep(1)
        opt_10 = page.locator('[role="option"]:has-text("10")')
        if await opt_10.count() > 0:
            await opt_10.first.click()
            print("Selected Rubric count '10' in UI!", flush=True)
        await asyncio.sleep(1)

    # Click DELIVERABLE AUTOQC accordion header to expand
    header = page.locator('div.cursor-pointer:has-text("DELIVERABLE AUTOQC")')
    if await header.count() > 0:
        await header.first.click()
        await asyncio.sleep(1)

    # Click Run AutoQC
    run_btn = page.locator('button:has-text("Run AutoQC")')
    if await run_btn.count() > 0:
        await run_btn.first.click()
        print("Clicked Run AutoQC successfully!", flush=True)

        # Monitor run
        start = time.time()
        for c in range(40):
            await asyncio.sleep(4)
            info = await page.evaluate("""() => {
                const body = document.body.innerText;
                const isRunning = body.includes('AutoQC is running') || body.includes('Compiling');
                
                const runBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText && (b.innerText.includes('Latest run') || b.innerText.includes('run ·')));
                const runText = runBtn ? runBtn.innerText.trim() : '';

                const passed = body.match(/(\\d+)\\s*passed/i);
                const major = body.match(/(\\d+)\\s*major/i);
                const minor = body.match(/(\\d+)\\s*minor/i);

                return { isRunning, runText, passed: passed ? passed[0] : null, major: major ? major[0] : null, minor: minor ? minor[0] : null };
            }""")
            elapsed = int(time.time() - start)
            print(f"[{elapsed}s] isRunning={info['isRunning']} | run={info['runText']} | passed={info['passed']} | major={info['major']} | minor={info['minor']}", flush=True)

            if not info['isRunning'] and c >= 2:
                print("AutoQC finished! Waiting 4s...", flush=True)
                await asyncio.sleep(4)
                break

    await page.screenshot(path='autoqc_100_percent_perfect.png')
    print("Saved autoqc_100_percent_perfect.png", flush=True)

    # Check Navigation checklist
    nav_btn = page.locator('button[title="Navigation"]')
    if await nav_btn.count() > 0:
        await nav_btn.first.click(force=True)
        await asyncio.sleep(2)
        await page.screenshot(path='navigation_checklist_100_percent.png')
        print("Saved navigation_checklist_100_percent.png", flush=True)

    await p.stop()
    print("Done!", flush=True)

if __name__ == '__main__':
    asyncio.run(apply_perfect_calibration())
