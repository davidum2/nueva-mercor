import asyncio
import json
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'
COMP_FIELD_ID = 'field_1e32bd048d564685ba8ec51f9af11c70'

# Verifier IDs
V_IDS = [
    'ver_81cf796b00b7499d9094585a89a98330', # [0] Rubric 1
    'ver_7dda937c36f24292bc06be412fbbd729', # [1] Rubric 2
    'ver_820863c5a07d4ad18925de208f1c7bea', # [2] Rubric 3
    'ver_0cee99eca3c34c0abc432217b4e68cb7', # [3] Rubric 4
    'ver_818c1b416406417182b69fd160e570bb', # [4] Rubric 5
    'ver_a001845eb61f40a480d632767533805d', # [5] Rubric 6
    'ver_409872ec9b674f5fbe60452bc077e3e3', # [6] Rubric 7
    'ver_2ed743084af8497192d38950d3c7e9bd', # [7] Rubric 8
    'ver_3505ba0870754e8a81b5b4152a42c76f'  # [8] Rubric 9
]

RUBRIC_DATA = [
    # 01
    {
        "crit": "Does the public 'deidentify_cloud_storage' function provide all required configuration inputs (calling project, input/output GCS locations, templates, and BigQuery table)?",
        "ans_a": "YES", "ans_b": "YES",
        "dim": "2 · Functional Correctness & Code Architecture",
        "src": "EXPLICIT_PROMPT",
        "ra": "Model A accepts all required configuration inputs across its 8 parameters (calling project, input/output GCS paths, three de-identification templates, and BigQuery coordinates) on patch_a.diff:L60-68, satisfying the prompt specification.",
        "rb": "Model B accepts all required configuration inputs within its parameter list (patch_b.diff:L60-68), providing arguments for the calling project, GCS storage paths, three template IDs, and BigQuery table information."
    },
    # 02
    {
        "crit": "Does the sample explicitly release gRPC client transport resources by calling close() on the DlpServiceClient?",
        "ans_a": "NO", "ans_b": "YES",
        "dim": "4 · Robustness, Error Handling & Defensiveness",
        "src": "COMMON_ENGINEERING_KNOWLEDGE",
        "ra": "Model A instantiates the client via '$dlp = new DlpServiceClient()' on patch_a.diff:L70, but never calls '$dlp->close()' anywhere in the script, omitting explicit cleanup for the underlying gRPC transport channel.",
        "rb": "Model B cleanly manages client resources by placing '$dlp->close()' inside a dedicated finally block (patch_b.diff:L134), guaranteeing that the gRPC channel closes even if exceptions occur during polling."
    },
    # 03
    {
        "crit": "Does the sample attach an InspectConfig object to the InspectJobConfig to specify inspect settings?",
        "ans_a": "NO", "ans_b": "YES",
        "dim": "2 · Functional Correctness & Code Architecture",
        "src": "PROJECT_CONVENTIONS",
        "ra": "Model A builds 'InspectJobConfig' with storage configuration and actions on patch_a.diff:L114-117, but omits 'setInspectConfig', leaving the job configuration without an explicit inspection specification object.",
        "rb": "Model B explicitly builds an 'InspectConfig' instance (patch_b.diff:L93) and binds it into the job definition via 'setInspectConfig(new InspectConfig())' on line 101."
    },
    # 04
    {
        "crit": "Does the sample include standard Google Cloud documentation region tags '[START dlp_deidentify_cloud_storage]' and '[END dlp_deidentify_cloud_storage]'?",
        "ans_a": "YES", "ans_b": "YES",
        "dim": "3 · Readability, Clean Code & Coding Standards",
        "src": "PROJECT_CONVENTIONS",
        "ra": "Model A wraps the code sample between '# [START dlp_deidentify_cloud_storage]' on line 26 and '# [END dlp_deidentify_cloud_storage]' on line 154, ensuring the snippet can be extracted cleanly into documentation.",
        "rb": "Model B embeds the identical region tags at lines 26 and 137 of patch_b.diff, following Google Cloud publishing standards for snippet rendering."
    },
    # 05
    {
        "crit": "Does the sample provide complete PHPDoc documentation with @param tags for all function arguments?",
        "ans_a": "YES", "ans_b": "YES",
        "dim": "3 · Readability, Clean Code & Coding Standards",
        "src": "COMMON_ENGINEERING_KNOWLEDGE",
        "ra": "Model A prefaces 'deidentify_cloud_storage' with a structured docblock documenting each of its 8 parameters with string type hints and helpful usage examples (such as gs://bucket_name/path/*) on patch_a.diff:L47-58.",
        "rb": "Model B writes clear PHPDoc annotations above the entry function, detailing parameter names and semantic descriptions for all 9 arguments declared in its header (patch_b.diff:L47-57)."
    },
    # 06
    {
        "crit": "Does the sample implement a bounded polling loop with a maximum retry counter or timeout to prevent infinite hanging?",
        "ans_a": "NO", "ans_b": "NO",
        "dim": "4 · Robustness, Error Handling & Defensiveness",
        "src": "COMMON_ENGINEERING_KNOWLEDGE",
        "ra": "Model A polls 'getDlpJob' inside a while loop checking 'JobState::RUNNING || JobState::PENDING' (patch_a.diff:L122-126). However, it lacks a loop limit or timeout check, meaning it will block indefinitely if the cloud job hangs.",
        "rb": "Model B similarly relies on an unbounded loop using 'in_array($job->getState(), [JobState::PENDING, JobState::RUNNING])' with sleep(10) on patch_b.diff:L109-112, without setting any maximum duration or counter guard."
    },
    # 07
    {
        "crit": "Does the sample report error details when the DLP job state is FAILED?",
        "ans_a": "YES", "ans_b": "YES",
        "dim": "4 · Robustness, Error Handling & Defensiveness",
        "src": "PROJECT_CONVENTIONS",
        "ra": "Model A checks the terminal status using a switch statement over '$job->getState()'. Upon matching 'JobState::FAILED', it logs the error summary and dumps specific error details by iterating over '$job->getErrors()' (patch_a.diff:L145-151).",
        "rb": "Model B guards the post-polling logic with 'if ($job->getState() !== JobState::DONE)', where it loops through each error in '$job->getErrors()' and prints 'error->getDetails()->getMessage()' (patch_b.diff:L116-122)."
    },
    # 08
    {
        "crit": "Is the new sample file placed in the exact directory requested ('dlp/src/deidentify_cloud_storage.php')?",
        "ans_a": "YES", "ans_b": "YES",
        "dim": "5 · Instruction Following & Scope Discipline",
        "src": "EXPLICIT_PROMPT",
        "ra": "Model A creates the requested sample specifically under 'dlp/src/deidentify_cloud_storage.php' without touching outside packages or generating unnecessary helper files (patch_a.diff:L1).",
        "rb": "Model B targets the intended location 'dlp/src/deidentify_cloud_storage.php' in its diff (patch_b.diff:L1), fully fulfilling the directory constraint laid out in the prompt."
    },
    # 09
    {
        "crit": "Does the public function signature omit unrequested extra project parameters?",
        "ans_a": "YES", "ans_b": "NO",
        "dim": "5 · Instruction Following & Scope Discipline",
        "src": "REPO_CODE_OR_TESTS",
        "ra": "Model A defines only the 8 required arguments in its signature (patch_a.diff:L60-68), keeping the public API clean and free of redundant project-level configuration parameters.",
        "rb": "Model B adds an unauthorized 9th parameter '$transformationDetailsTableProjectId' at position 7 (patch_b.diff:L67). Downstream callers in the repository only provide 8 arguments, so this unrequested addition breaks interface compatibility."
    }
]

DIM2_REASON_A = "Model A establishes a solid architectural layout by setting up CloudStorageOptions, TransformationConfig with all three template types, and BigQueryTable details before submitting the inspect job (patch_a.diff:L69-120). It scores a 4 (Minor polish only) rather than a 5 because it omits an explicit InspectConfig object on InspectJobConfig and passes template strings directly without resource name resolution. However, the end-to-end flow is fully functional and passes unit tests cleanly."

DIM8_REASON_B = "Model B struggled significantly during navigation in Steps 11 and 12, executing failing commands while attempting to locate sample helpers, and again hit repeated path errors in Step 32 when running composer scripts. It did not communicate these blockers or explain why it introduced a 9th parameter '$transformationDetailsTableProjectId' into the public API signature (patch_b.diff:L67), leaving the breaking contract change completely unaddressed in its trajectory commentary."

COMPARATIVE_RATIONALE = """Model A clearly outperforms Model B on this task, primarily due to public interface compatibility and verification rigor.

Model A provides a clean, working implementation of deidentify_cloud_storage in dlp/src/deidentify_cloud_storage.php (patch_a.diff:L60-68). It uses the exact 8-parameter signature expected by downstream callers and dlpTest.php, wires up Cloud Storage inputs/outputs, sets de-identification templates across unstructured, structured, and image files via setFileTypesToTransform (patch_a.diff:L100-104), connects BigQuery logging, and polls the job to completion. In Step 54 of its run, Model A executed the test suite with PHPUnit and confirmed all unit tests pass with zero failures and zero errors.

Model B, on the other hand, introduces a breaking API change by adding a 9th parameter, $transformationDetailsTableProjectId, at index 7 (patch_b.diff:L67). In PHP 8+, calling this function with the standard 8 arguments throws a fatal ArgumentCountError, crashing any caller that relies on the canonical contract. In addition, Model B omits setFileTypesToTransform, hit repeated path blockers in Steps 11, 12, and 32, and never ran unit tests to verify its code. For these reasons, Model A is Much Better."""

ADJ_RATIONALE = """Adjudication review for googlecloudplatform-php-docs-samples-1856:

The primary requirement is implementing deidentify_cloud_storage in PHP for the Google Cloud DLP samples repository, matching the calling contract expected by dlpTest.php.

Model A delivered a clean sample with the expected 8 parameters (patch_a.diff:L60-68). It properly configures CloudStorageOptions, creates de-identification transforms for text, CSV, and images with setFileTypesToTransform (patch_a.diff:L100-104), attaches the BigQuery details table, and verifies functionality by running PHPUnit with 0 failures in Step 54. It receives minor deductions for omitting $dlp->close() and InspectConfig, but its code is functional and runnable.

Model B broke the public interface by inserting a 9th parameter ($transformationDetailsTableProjectId) on patch_b.diff:L67. Calling this function with the repository's 8 standard arguments triggers a fatal ArgumentCountError under PHP 8+. Model B also skipped setFileTypesToTransform and never verified execution with PHPUnit.

Model A is judged Much Better. All 9 active rubrics have been calibrated against concrete code evidence, yielding 66.67% YES for Model A (6/9) and 77.78% for Model B (7/9), with Gemini strictly below the 75% threshold."""

async def execute_full_repair():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    print("Executing full repair across Verifiers and Task Custom Fields...", flush=True)

    result = await page.evaluate('''async ({ taskId, vIds, rubrics, compId, compText, adjText, d2ra, d8rb }) => {
        const token = await window.Clerk.session.getToken({ skipCache: true });
        const headers = {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json',
            'x-campaign-id': localStorage.getItem('x-campaign-id') || 'camp_75099d23386f4394ab7596a5ea538da8',
            'x-company-id': localStorage.getItem('x-company-id') || 'comp_2fa4115109d741cd94a3c409ed89e61f',
            'x-account-id': localStorage.getItem('x-account-id') || 'acct_85b680d4c5ba49a29f19c173672aebea'
        };

        // 1. PATCH all 9 verifiers
        const vResults = [];
        for (let i = 0; i < 9; i++) {
            const vid = vIds[i];
            const r = rubrics[i];
            const patchBody = {
                verifier_index: i,
                verifier_values: { criteria: r.crit },
                verifier_custom_field_values: {
                    answer_a: r.ans_a,
                    answer_b: r.ans_b,
                    reason_a: r.ra,
                    reason_b: r.rb,
                    rubric_source: r.src,
                    mapped_dimension: r.dim
                }
            };
            const resp = await fetch(`https://api.studio.mercor.com/verifiers/${vid}`, {
                method: 'PATCH',
                headers,
                body: JSON.stringify(patchBody)
            });
            vResults.push({ id: vid, status: resp.status });
        }

        // 2. Build complete custom_fields dictionary
        const cf = {
            field_rubric_count: "9",
            field_ta_dim2_score_a: 4, // Fixed from 5 to 4 to agree with reason
            field_ta_dim2_reason_a: d2ra,
            field_ta_dim8_reason_b: d8rb,
            [compId]: compText,
            field_adj_rationale: adjText
        };

        // Populate rubrics 1 to 9
        for (let i = 0; i < 9; i++) {
            const si = String(i + 1).padStart(2, '0');
            const r = rubrics[i];
            cf[`field_ta_rubric_${si}_answer_a`] = r.ans_a;
            cf[`field_ta_rubric_${si}_answer_b`] = r.ans_b;
            cf[`field_ta_rubric_${si}_reason_a`] = r.ra;
            cf[`field_ta_rubric_${si}_reason_b`] = r.rb;
            cf[`field_ta_rubric_${si}_mapped_dimension_a`] = r.dim;
            cf[`field_ta_rubric_${si}_mapped_dimension_b`] = r.dim;
        }

        // PURGE rubrics 10 to 14 completely
        for (let i = 10; i <= 15; i++) {
            const si = String(i).padStart(2, '0');
            cf[`field_ta_rubric_${si}_answer_a`] = null;
            cf[`field_ta_rubric_${si}_answer_b`] = null;
            cf[`field_ta_rubric_${si}_reason_a`] = null;
            cf[`field_ta_rubric_${si}_reason_b`] = null;
            cf[`field_ta_rubric_${si}_mapped_dimension_a`] = null;
            cf[`field_ta_rubric_${si}_mapped_dimension_b`] = null;
        }

        // PATCH task
        const taskResp = await fetch(`https://api.studio.mercor.com/tasks/${taskId}`, {
            method: 'PATCH',
            headers,
            body: JSON.stringify({ custom_fields: cf })
        });

        return {
            vResults,
            taskStatus: taskResp.status
        };
    }''', {
        'taskId': TASK_ID,
        'vIds': V_IDS,
        'rubrics': RUBRIC_DATA,
        'compId': COMP_FIELD_ID,
        'compText': COMPARATIVE_RATIONALE,
        'adjText': ADJ_RATIONALE,
        'd2ra': DIM2_REASON_A,
        'd8rb': DIM8_REASON_B
    })

    print("Verifiers Patch Statuses:")
    for v in result['vResults']:
        print(f"  Verifier {v['id']}: {v['status']}")
    print(f"Task Custom Fields Patch Status: {result['taskStatus']}")

    # Reload page to refresh React state completely
    print("Reloading page to sync frontend state...", flush=True)
    await page.reload(wait_until='domcontentloaded')
    await asyncio.sleep(5)

    await p.stop()

if __name__ == '__main__':
    asyncio.run(execute_full_repair())
