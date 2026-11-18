import asyncio
import json
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True)

TASK_ID = "task_a6c044440a2b440a9d578ad5c375ad94"

async def run_complete_injection():
    print("Starting completion injection...", flush=True)
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [pg for pg in browser.contexts[0].pages if 'mercor.com' in pg.url and 'sign-in' not in pg.url][0]
    print(f"Connected to page: {page.url}", flush=True)

    with open('selected_rubrics_13.json', 'r', encoding='utf-8') as f:
        rubrics = json.load(f)

    # Dimensions data
    dim_data = {
        "dim2_score_a": 4,
        "dim2_reason_a": "Model A cleanly implements the required deidentify_cloud_storage function with the exact 8-parameter signature expected by downstream callers and dlpTest.php (patch_a.diff:L60-68). It correctly instantiates DlpServiceClient (patch_a.diff:L70), sets up CloudStorageOptions with setFileSet and setUrl (patch_a.diff:L74-75), configures transformation details in BigQueryTable (patch_a.diff:L87-90), specifies Deidentify file types (patch_a.diff:L100-104), and constructs InspectJobConfig with actions. It receives a minor penalty for passing raw string template names instead of resolving resource paths via DlpServiceBaseClient::projectDeidentifyTemplateName.",
        
        "dim3_score_a": 5,
        "dim3_reason_a": "Model A follows official Google Cloud sample conventions flawlessly. It includes standard documentation region tags '# [START dlp_deidentify_cloud_storage]' and '# [END dlp_deidentify_cloud_storage]' (patch_a.diff:L33, L159), declares the proper namespace Google\\Cloud\\Samples\\Dlp (patch_a.diff:L31), provides comprehensive PHPDoc type annotations for all 8 parameters (patch_a.diff:L50-58), and appends the standard CLI sample execution harness calling execute_sample (patch_a.diff:L162-163).",
        
        "dim4_score_a": 3,
        "dim4_reason_a": "Model A provides descriptive error reporting on failure states by switching on $job->getState() and dumping $error->getDetails() for JobState::FAILED (patch_a.diff:L145-151), and handles zero findings cleanly (patch_a.diff:L134). However, its polling loop 'while ($job->getState() == JobState::RUNNING || ...)' is completely unbounded without an attempt limit or timeout (patch_a.diff:L122-126), and it omits $dlp->close() in a finally block to release gRPC transport channels.",
        
        "dim5_score_a": 5,
        "dim5_reason_a": "Model A exhibits perfect instruction following and scope discipline. It creates only the requested sample file at 'dlp/src/deidentify_cloud_storage.php' without touching existing repository files (patch_a.diff). It exposes the exact public function name 'deidentify_cloud_storage' required by Additional Requirements, respects the 8 requested parameters, and prints the job name and sensitive infoType finding counts upon completion (patch_a.diff:L129-142).",
        
        "dim6_score_a": 4,
        "dim6_reason_a": "Model A demonstrated systematic planning and codebase exploration. Across Steps 1 to 28, it examined existing DLP samples in dlp/src/ (such as deidentify_dates.php and inspect_bigquery.php) to adopt canonical patterns, inspected sample_helpers.php in Step 29, checked DLP JobState protobuf constants in Step 39, and inspected dlpTest.php in Step 53 without getting stuck in failing directory lookups.",
        
        "dim7_score_a": 4,
        "dim7_reason_a": "Model A executed thorough validation during its trajectory. In Step 50, it ran PHP syntax linting ('php -l /workspace/repo/dlp/src/deidentify_cloud_storage.php') confirming zero syntax errors. In Step 52, it tested CLI argument handling. In Step 54, it ran PHPUnit against the test suite, and in Step 55, it validated reflection confirming the function existence and 8 parameters before confirming git status in Step 56.",
        
        "dim8_score_a": 5,
        "dim8_reason_a": "Model A communicates concisely and professionally throughout its execution. It documented its plan during exploration steps without spamming or going silent, and delivered a well-structured final answer (final_answer_a.txt) that clearly outlines Configuration, Job Submission & Polling, and Summary Reporting without conversational filler.",
        
        "dim9_score_a": 5,
        "dim9_reason_a": "Model A's final deliverable summary is completely factual, honest, and precise. It accurately references the created file 'dlp/src/deidentify_cloud_storage.php', describes the exact public function name, explicitly notes structured data support for CSV, and avoids hallucinating test results or claiming unexecuted modifications (final_answer_a.txt).",
        
        # Side B
        "dim2_score_b": 1,
        "dim2_reason_b": "Model B suffers a fatal contract defect. On patch_b.diff:L67, it adds an unauthorized 9th parameter '$transformationDetailsTableProjectId' at position 7, shifting $datasetId and $tableId. When downstream callers or dlpTest.php invoke the function with 8 arguments, PHP 8 throws an uncaught fatal ArgumentCountError, crashing execution. Furthermore, Model B omits setFileTypesToTransform on the Deidentify action (patch_b.diff:L92-96).",
        
        "dim3_score_b": 4,
        "dim3_reason_b": "Model B follows coding standards adequately by including region tags (patch_b.diff:L33, L141), namespace declarations, and PHPDoc blocks. However, its parameter documentation reflects the broken 9-parameter signature (patch_b.diff:L57), and the Apache license year is set inconsistently to 2026 on line 10.",
        
        "dim4_score_b": 3,
        "dim4_reason_b": "Model B demonstrates good defensive practice by wrapping client calls in a try-finally block and ensuring $dlp->close() is invoked (patch_b.diff:L138). However, like Model A, its polling loop is unbounded without maximum retries (patch_b.diff:L109-112), and its signature defect prevents the function from ever executing successfully when called by tests.",
        
        "dim5_score_b": 1,
        "dim5_reason_b": "Model B violates explicit scope discipline. While it places the file in dlp/src/deidentify_cloud_storage.php, it breaks the core interface contract by introducing an unrequested 9th parameter '$transformationDetailsTableProjectId' (patch_b.diff:L67). It also fails to configure file types to transform as requested by the sample workflow.",
        
        "dim6_score_b": 2,
        "dim6_reason_b": "Model B exhibited severe tool and navigation thrashing. In Steps 11, 12, and 32, it repeatedly executed failing commands attempting to access nonexistent directories ('/workspace/repo' and '/workspace'). Despite reading golden.patch and solve.sh in Step 16 and Step 29, it failed to align its signature with the 8-parameter interface established in dlpTest.php.",
        
        "dim7_score_b": 2,
        "dim7_reason_b": "Model B performed minimal verification. While it ran a syntax check in Step 34, it failed to execute PHPUnit or verify compatibility with dlpTest.php, admitting in its final answer that it could not run tests because vendor/bin/phpunit was not located. It never ran reflection to check parameter counts.",
        
        "dim8_score_b": 3,
        "dim8_reason_b": "Model B provided structured communication in its final summary. However, it failed to communicate or diagnose its path navigation blockers effectively during execution, and did not explain why it added a 9th parameter that contradicted the prompt's parameter requirements.",
        
        "dim9_score_b": 2,
        "dim9_reason_b": "Model B's final summary is deceptive regarding its public API signature. In final_answer_b.txt:L5, it writes 'deidentify_cloud_storage(...)' with an ellipsis, concealing the fact that it introduced an extraneous 9th parameter that broke compatibility with existing tests and callers.",
        
        "final_score_a": 4,
        "final_score_b": 1,
        "comparative_rationale": "Model A is significantly superior to Model B across functional correctness, interface compliance, and test suite execution.\n\nModel A correctly implements the public function 'deidentify_cloud_storage' in 'dlp/src/deidentify_cloud_storage.php' with the exact 8-parameter signature required by downstream callers and dlpTest.php (patch_a.diff:L60-68). It configures the Cloud Storage input and output, sets up de-identification templates for unstructured, structured (CSV), and image files via setFileTypesToTransform (patch_a.diff:L100-104), connects the BigQuery details table, and polls the job to completion, successfully passing unit test validation.\n\nIn contrast, Model B introduces a fatal interface defect by injecting an unrequested 9th parameter '$transformationDetailsTableProjectId' at position 7 (patch_b.diff:L67). In PHP 8+, calling this function with 8 arguments causes an uncaught fatal ArgumentCountError, crashing downstream callers. Additionally, Model B omits setFileTypesToTransform, suffered repeated directory path failures in Steps 11, 12, and 32, and failed to run test suite verification. Therefore, Model A is clearly the better rollout."
    }

    result = await page.evaluate("""async ({ taskId, rubrics, dims }) => {
        const getHeaders = async () => {
            const token = await window.Clerk.session.getToken({ skipCache: true });
            return {
                'Authorization': 'Bearer ' + token,
                'Content-Type': 'application/json',
                'x-campaign-id': localStorage.getItem('x-campaign-id') || 'camp_75099d23386f4394ab7596a5ea538da8',
                'x-company-id': localStorage.getItem('x-company-id') || 'comp_2fa4115109d741cd94a3c409ed89e61f',
                'x-account-id': localStorage.getItem('x-account-id') || 'acct_85b680d4c5ba49a29f19c173672aebea'
            };
        };

        // 1. Fetch current verifiers to know what indices exist
        const checkHeaders = await getHeaders();
        const curR = await fetch(`https://api.studio.mercor.com/verifiers/task/${taskId}`, { headers: checkHeaders });
        const curData = await curR.json();
        const existingVerifiers = curData.verifiers || [];
        const existingIndices = new Set(existingVerifiers.map(v => v.verifier_index));

        const createdResults = [];
        // 2. Create missing verifiers (indices 0 to 12)
        for (let i = 0; i < rubrics.length; i++) {
            if (existingIndices.has(i)) {
                createdResults.push({ idx: i, skipped: true, note: 'Already exists' });
                continue;
            }
            const r = rubrics[i];
            const body = {
                task_id: taskId,
                eval_config_id: 'evalcfg_prompt_specific_rubric',
                verifier_values: {
                    criteria: r.rubric_text
                },
                verifier_custom_field_values: {
                    answer_a: r.answer_a,
                    answer_b: r.answer_b,
                    reason_a: r.reason_a,
                    reason_b: r.reason_b,
                    rubric_source: r.source,
                    mapped_dimension: `${r.dimension} · ${r.dimension_name}`
                },
                verifier_index: i,
                verifier_dependencies: []
            };

            const postHeaders = await getHeaders();
            const postR = await fetch('https://api.studio.mercor.com/verifiers/', {
                method: 'POST',
                headers: postHeaders,
                body: JSON.stringify(body)
            });
            const postData = await postR.json();
            createdResults.push({ idx: i, status: postR.status, ok: postR.ok, id: postData.verifier_id });
        }

        // 3. Prepare custom_fields updates on task
        const custom_fields = {
            field_rubric_count: String(rubrics.length),
            field_ta_final_quality_score_a: dims.final_score_a,
            field_ta_final_quality_score_b: dims.final_score_b,
            field_e511999a150a45c2b7145f808103d78c: "A_BETTER",
            field_adj_rationale: dims.comparative_rationale,
            
            // Dimensions 2-9 Side A
            field_ta_dim2_score_a: dims.dim2_score_a,
            field_ta_dim2_reason_a: dims.dim2_reason_a,
            field_ta_dim3_score_a: dims.dim3_score_a,
            field_ta_dim3_reason_a: dims.dim3_reason_a,
            field_ta_dim4_score_a: dims.dim4_score_a,
            field_ta_dim4_reason_a: dims.dim4_reason_a,
            field_ta_dim5_score_a: dims.dim5_score_a,
            field_ta_dim5_reason_a: dims.dim5_reason_a,
            field_ta_dim6_score_a: dims.dim6_score_a,
            field_ta_dim6_reason_a: dims.dim6_reason_a,
            field_ta_dim7_score_a: dims.dim7_score_a,
            field_ta_dim7_reason_a: dims.dim7_reason_a,
            field_ta_dim8_score_a: dims.dim8_score_a,
            field_ta_dim8_reason_a: dims.dim8_reason_a,
            field_ta_dim9_score_a: dims.dim9_score_a,
            field_ta_dim9_reason_a: dims.dim9_reason_a,

            // Dimensions 2-9 Side B
            field_ta_dim2_score_b: dims.dim2_score_b,
            field_ta_dim2_reason_b: dims.dim2_reason_b,
            field_ta_dim3_score_b: dims.dim3_score_b,
            field_ta_dim3_reason_b: dims.dim3_reason_b,
            field_ta_dim4_score_b: dims.dim4_score_b,
            field_ta_dim4_reason_b: dims.dim4_reason_b,
            field_ta_dim5_score_b: dims.dim5_score_b,
            field_ta_dim5_reason_b: dims.dim5_reason_b,
            field_ta_dim6_score_b: dims.dim6_score_b,
            field_ta_dim6_reason_b: dims.dim6_reason_b,
            field_ta_dim7_score_b: dims.dim7_score_b,
            field_ta_dim7_reason_b: dims.dim7_reason_b,
            field_ta_dim8_score_b: dims.dim8_score_b,
            field_ta_dim8_reason_b: dims.dim8_reason_b,
            field_ta_dim9_score_b: dims.dim9_score_b,
            field_ta_dim9_reason_b: dims.dim9_reason_b
        };

        // Add rubrics custom_fields
        for (let i = 0; i < rubrics.length; i++) {
            const r = rubrics[i];
            const num = String(i + 1).padStart(2, '0');
            const dimStr = `${r.dimension} · ${r.dimension_name}`;
            custom_fields[`field_ta_rubric_${num}_answer_a`] = r.answer_a;
            custom_fields[`field_ta_rubric_${num}_reason_a`] = r.reason_a;
            custom_fields[`field_ta_rubric_${num}_mapped_dimension_a`] = dimStr;

            custom_fields[`field_ta_rubric_${num}_answer_b`] = r.answer_b;
            custom_fields[`field_ta_rubric_${num}_reason_b`] = r.reason_b;
            custom_fields[`field_ta_rubric_${num}_mapped_dimension_b`] = dimStr;
        }

        // 4. Send PATCH to update task
        const patchHeaders = await getHeaders();
        const patchR = await fetch(`https://api.studio.mercor.com/tasks/${taskId}`, {
            method: 'PATCH',
            headers: patchHeaders,
            body: JSON.stringify({ custom_fields })
        });
        const patchData = await patchR.json();

        // 5. Verify final verifiers count
        const verifyHeaders = await getHeaders();
        const finR = await fetch(`https://api.studio.mercor.com/verifiers/task/${taskId}`, { headers: verifyHeaders });
        const finData = await finR.json();

        return {
            createdResults,
            patchStatus: patchR.status,
            patchOk: patchR.ok,
            updatedAt: patchData.updated_at,
            finalVerifiersCount: (finData.verifiers || []).length,
            finalVerifiers: (finData.verifiers || []).map(v => ({
                id: v.verifier_id,
                idx: v.verifier_index,
                ans_a: v.verifier_custom_field_values?.answer_a,
                ans_b: v.verifier_custom_field_values?.answer_b
            }))
        };
    }""", { "taskId": TASK_ID, "rubrics": rubrics, "dims": dim_data })

    print("=== FINAL INJECTION RESULT ===", flush=True)
    print("Created/Skipped verifiers:", flush=True)
    for cr in result.get('createdResults', []):
        print(f"  Rubric {cr.get('idx', 0)+1:02d}: Status={cr.get('status')} | OK={cr.get('ok')} | Note={cr.get('note')}", flush=True)
    print(f"Task PATCH Status: {result.get('patchStatus')} | OK: {result.get('patchOk')}", flush=True)
    print(f"Task updated_at: {result.get('updatedAt')}", flush=True)
    print(f"Final Verifiers in Task: {result.get('finalVerifiersCount')}", flush=True)
    for v in result.get('finalVerifiers', []):
        print(f"  Ver {v.get('idx')+1:02d} (ID: {v.get('id')}): A={v.get('ans_a')} | B={v.get('ans_b')}", flush=True)

    with open('final_injection_result.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)

    await p.stop()
    print("Done!", flush=True)

if __name__ == '__main__':
    asyncio.run(run_complete_injection())
