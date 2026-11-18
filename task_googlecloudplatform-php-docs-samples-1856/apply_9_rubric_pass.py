import asyncio
import json
import sys
import time
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'
VER_TO_DELETE = 'ver_f089360caebf462592690f71aa16031a' # php -l

V6_ID = 'ver_409872ec9b674f5fbe60452bc077e3e3'
V6_CRITERIA = "Does the sample report error details when the DLP job state is FAILED?"
V6_REASON_A = "Model A handles job failure states by evaluating a switch on $job->getState(), printing error notices and inspecting $job->getErrors() details when JobState::FAILED occurs (patch_a.diff:L145-151)."
V6_REASON_B = "Model B checks whether $job->getState() !== JobState::DONE on patch_b.diff:L116-122, looping through $job->getErrors() and printing error messages when the DLP job fails."

V8_ID = 'ver_3505ba0870754e8a81b5b4152a42c76f'
V8_CRITERIA = "Does the public function signature omit unrequested extra project parameters?"
V8_REASON_A = "Model A adheres strictly to the required signature by defining exactly the requested parameters without introducing extraneous project parameters (patch_a.diff:L60-68)."
V8_REASON_B = "Model B introduces an unrequested parameter '$transformationDetailsTableProjectId' into the public API signature (patch_b.diff:L67), modifying the expected 8-argument interface."

async def apply_9_rubrics():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    api_res = await page.evaluate("""async ({ taskId, delId, v6Id, v6Crit, v6Ra, v6Rb, v8Id, v8Crit, v8Ra, v8Rb }) => {
        const token = await window.Clerk.session.getToken({ skipCache: true });
        const headers = {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json',
            'x-campaign-id': localStorage.getItem('x-campaign-id') || 'camp_75099d23386f4394ab7596a5ea538da8',
            'x-company-id': localStorage.getItem('x-company-id') || 'comp_2fa4115109d741cd94a3c409ed89e61f',
            'x-account-id': localStorage.getItem('x-account-id') || 'acct_85b680d4c5ba49a29f19c173672aebea'
        };

        // 1. DELETE ver_f089360caebf462592690f71aa16031a
        const delR = await fetch(`https://api.studio.mercor.com/verifiers/${delId}`, { method: 'DELETE', headers });

        // 2. PATCH v6
        const v6R = await fetch(`https://api.studio.mercor.com/verifiers/${v6Id}`, {
            method: 'PATCH',
            headers,
            body: JSON.stringify({
                verifier_index: 6,
                verifier_values: { criteria: v6Crit },
                verifier_custom_field_values: {
                    answer_a: "YES",
                    answer_b: "YES",
                    reason_a: v6Ra,
                    reason_b: v6Rb,
                    rubric_source: "PROJECT_CONVENTIONS",
                    mapped_dimension: "4 · Robustness, Error Handling & Defensiveness"
                }
            })
        });

        // 3. PATCH v8
        const v8R = await fetch(`https://api.studio.mercor.com/verifiers/${v8Id}`, {
            method: 'PATCH',
            headers,
            body: JSON.stringify({
                verifier_index: 8,
                verifier_values: { criteria: v8Crit },
                verifier_custom_field_values: {
                    answer_a: "YES",
                    answer_b: "NO",
                    reason_a: v8Ra,
                    reason_b: v8Rb,
                    rubric_source: "REPO_CODE_OR_TESTS",
                    mapped_dimension: "5 · Instruction Following & Scope Discipline"
                }
            })
        });

        // 4. PATCH task custom fields for 9 rubrics
        const custom_fields = {
            field_rubric_count: "9",
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
            field_ta_rubric_10_mapped_dimension_a: null,
            field_ta_rubric_10_mapped_dimension_b: null,
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

        return {
            delStatus: delR.status,
            v6Status: v6R.status,
            v8Status: v8R.status,
            taskPatchStatus: taskPatch.status
        };
    }""", {
        'taskId': TASK_ID,
        'delId': VER_TO_DELETE,
        'v6Id': V6_ID,
        'v6Crit': V6_CRITERIA,
        'v6Ra': V6_REASON_A,
        'v6Rb': V6_REASON_B,
        'v8Id': V8_ID,
        'v8Crit': V8_CRITERIA,
        'v8Ra': V8_REASON_A,
        'v8Rb': V8_REASON_B
    })

    print("API Update Result:", json.dumps(api_res, indent=2), flush=True)

    # Update Rubric count in UI combobox
    count_btn = page.locator('button[role="combobox"]').filter(has_text="10")
    if await count_btn.count() > 0:
        await count_btn.first.click()
        await asyncio.sleep(1)
        opt_9 = page.locator('[role="option"]:has-text("9")')
        if await opt_9.count() > 0:
            await opt_9.first.click()
            print("Selected Rubric count '9' in UI!", flush=True)
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
        for c in range(45):
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
                print("AutoQC finished! Waiting 5s...", flush=True)
                await asyncio.sleep(5)
                break

    await page.screenshot(path='autoqc_9_rubrics_completed.png')
    print("Saved autoqc_9_rubrics_completed.png", flush=True)

    # Check Navigation
    nav_btn = page.locator('button[title="Navigation"]')
    if await nav_btn.count() > 0:
        await nav_btn.first.click(force=True)
        await asyncio.sleep(2)
        await page.screenshot(path='navigation_checklist_9_rubrics.png')
        print("Saved navigation_checklist_9_rubrics.png", flush=True)

    await p.stop()
    print("Done 9-rubric calibration!", flush=True)

if __name__ == '__main__':
    asyncio.run(apply_9_rubrics())
