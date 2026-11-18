import json

questions = [
    # ==========================================
    # DIMENSION 2: Functional Correctness & Code Architecture (10 questions)
    # ==========================================
    {
        "id": "Q01",
        "dimension": 2,
        "dimension_name": "Functional Correctness & Code Architecture",
        "source": "EXPLICIT_PROMPT",
        "question": "Does the sample implement the required 'deidentify_cloud_storage' function with exactly 8 parameters matching downstream test callers?",
        "expected_a": "YES",
        "expected_b": "NO",
        "note_a": "Model A exposes exactly 8 parameters: $callingProjectId, $inputGcsUri, $outputGcsUri, $deidentifyTemplate, $structuredDeidentifyTemplate, $imageRedactTemplate, $datasetId, $tableId (patch_a.diff:L60-68).",
        "note_b": "Model B adds an extraneous 9th parameter '$transformationDetailsTableProjectId' at position 7, breaking the 8-argument call in dlpTest.php with an uncaught ArgumentCountError (patch_b.diff:L60-70)."
    },
    {
        "id": "Q02",
        "dimension": 2,
        "dimension_name": "Functional Correctness & Code Architecture",
        "source": "EXPLICIT_PROMPT",
        "question": "Does the sample configure CloudStorageOptions with the input Cloud Storage URI using setFileSet and setUrl?",
        "expected_a": "YES",
        "expected_b": "YES",
        "note_a": "Model A sets CloudStorageOptions -> FileSet -> setUrl($inputGcsUri) on patch_a.diff:L73-75.",
        "note_b": "Model B sets CloudStorageOptions -> FileSet -> setUrl($inputGcsPath) on patch_b.diff:L76-78."
    },
    {
        "id": "Q03",
        "dimension": 2,
        "dimension_name": "Functional Correctness & Code Architecture",
        "source": "EXPLICIT_PROMPT",
        "question": "Does the sample configure the BigQuery destination table for transformation details with projectId, datasetId, and tableId?",
        "expected_a": "YES",
        "expected_b": "YES",
        "note_a": "Model A instantiates BigQueryTable setting projectId, datasetId, and tableId (patch_a.diff:L87-90).",
        "note_b": "Model B instantiates BigQueryTable setting projectId, datasetId, and tableId (patch_b.diff:L85-88)."
    },
    {
        "id": "Q04",
        "dimension": 2,
        "dimension_name": "Functional Correctness & Code Architecture",
        "source": "EXPLICIT_PROMPT",
        "question": "Does the sample configure separate de-identification templates for unstructured, structured, and image files on TransformationConfig?",
        "expected_a": "YES",
        "expected_b": "YES",
        "note_a": "Model A sets deidentifyTemplate, structuredDeidentifyTemplate, and imageRedactTemplate (patch_a.diff:L81-84).",
        "note_b": "Model B sets deidentifyTemplate, structuredDeidentifyTemplate, and imageRedactTemplate (patch_b.diff:L80-83)."
    },
    {
        "id": "Q05",
        "dimension": 2,
        "dimension_name": "Functional Correctness & Code Architecture",
        "source": "COMMON_ENGINEERING_KNOWLEDGE",
        "question": "Does the sample resolve template names using DlpServiceBaseClient::projectDeidentifyTemplateName rather than passing unvalidated raw strings?",
        "expected_a": "NO",
        "expected_b": "NO",
        "note_a": "Model A passes raw string template arguments directly to setDeidentifyTemplate without using projectDeidentifyTemplateName (patch_a.diff:L82-84).",
        "note_b": "Model B also passes raw strings directly without projectDeidentifyTemplateName resolution (patch_b.diff:L81-83)."
    },
    {
        "id": "Q06",
        "dimension": 2,
        "dimension_name": "Functional Correctness & Code Architecture",
        "source": "EXPLICIT_PROMPT",
        "question": "Does the sample explicitly configure the file types to transform on the Deidentify action object?",
        "expected_a": "YES",
        "expected_b": "NO",
        "note_a": "Model A calls setFileTypesToTransform with FileType::IMAGE, FileType::CSV, and FileType::TEXT_FILE (patch_a.diff:L100-104).",
        "note_b": "Model B completely omits setFileTypesToTransform on the Deidentify action (patch_b.diff:L92-96)."
    },
    {
        "id": "Q07",
        "dimension": 2,
        "dimension_name": "Functional Correctness & Code Architecture",
        "source": "COMMON_ENGINEERING_KNOWLEDGE",
        "question": "Does the sample attach an InspectConfig object to the InspectJobConfig to specify inspect settings?",
        "expected_a": "NO",
        "expected_b": "YES",
        "note_a": "Model A configures StorageConfig and Actions on InspectJobConfig but completely omits setInspectConfig (patch_a.diff:L110-112).",
        "note_b": "Model B attaches setInspectConfig(new InspectConfig()) on InspectJobConfig (patch_b.diff:L100)."
    },
    {
        "id": "Q08",
        "dimension": 2,
        "dimension_name": "Functional Correctness & Code Architecture",
        "source": "EXPLICIT_PROMPT",
        "question": "Does the sample configure the output Cloud Storage location on the Deidentify action via setCloudStorageOutput?",
        "expected_a": "YES",
        "expected_b": "YES",
        "note_a": "Model A calls setCloudStorageOutput($outputGcsUri) on patch_a.diff:L99.",
        "note_b": "Model B calls setCloudStorageOutput($outputGcsPath) on patch_b.diff:L95."
    },
    {
        "id": "Q09",
        "dimension": 2,
        "dimension_name": "Functional Correctness & Code Architecture",
        "source": "EXPLICIT_PROMPT",
        "question": "Does the sample submit the job via createDlpJob using the global locations parent path format 'projects/{projectId}/locations/global'?",
        "expected_a": "YES",
        "expected_b": "YES",
        "note_a": "Model A constructs $parent = 'projects/$callingProjectId/locations/global' and calls createDlpJob (patch_a.diff:L115-117).",
        "note_b": "Model B constructs $parent = 'projects/$callingProjectId/locations/global' and calls createDlpJob (patch_b.diff:L103-105)."
    },
    {
        "id": "Q10",
        "dimension": 2,
        "dimension_name": "Functional Correctness & Code Architecture",
        "source": "EXPLICIT_PROMPT",
        "question": "Does the sample iterate through infoTypeStats to print each detected sensitive infoType name and its occurrence count?",
        "expected_a": "YES",
        "expected_b": "YES",
        "note_a": "Model A loops over $infoTypeStats printing count and name via getInfoType()->getName() (patch_a.diff:L136-142).",
        "note_b": "Model B loops over $infoTypeStats printing count and name via getInfoType()->getName() (patch_b.diff:L130-136)."
    },

    # ==========================================
    # DIMENSION 3: Readability, Clean Code & Coding Standards (6 questions)
    # ==========================================
    {
        "id": "Q11",
        "dimension": 3,
        "dimension_name": "Readability, Clean Code & Coding Standards",
        "source": "ENVIRONMENT",
        "question": "Does the sample include standard Google Cloud documentation region tags '[START dlp_deidentify_cloud_storage]' and '[END dlp_deidentify_cloud_storage]'?",
        "expected_a": "YES",
        "expected_b": "YES",
        "note_a": "Model A includes [START dlp_deidentify_cloud_storage] on line 33 and [END dlp_deidentify_cloud_storage] on line 159 (patch_a.diff).",
        "note_b": "Model B includes [START dlp_deidentify_cloud_storage] on line 33 and [END dlp_deidentify_cloud_storage] on line 141 (patch_b.diff)."
    },
    {
        "id": "Q12",
        "dimension": 3,
        "dimension_name": "Readability, Clean Code & Coding Standards",
        "source": "ENVIRONMENT",
        "question": "Does the sample use the standard namespace 'Google\\Cloud\\Samples\\Dlp' matching other samples in dlp/src/?",
        "expected_a": "YES",
        "expected_b": "YES",
        "note_a": "Model A declares namespace Google\\Cloud\\Samples\\Dlp on line 31 (patch_a.diff).",
        "note_b": "Model B declares namespace Google\\Cloud\\Samples\\Dlp on line 31 (patch_b.diff)."
    },
    {
        "id": "Q13",
        "dimension": 3,
        "dimension_name": "Readability, Clean Code & Coding Standards",
        "source": "ENVIRONMENT",
        "question": "Does the sample provide complete PHPDoc documentation with @param tags for all function arguments?",
        "expected_a": "YES",
        "expected_b": "YES",
        "note_a": "Model A includes comprehensive PHPDoc block with @param string descriptions for all 8 parameters (patch_a.diff:L50-58).",
        "note_b": "Model B includes PHPDoc descriptions for its declared parameters (patch_b.diff:L50-59)."
    },
    {
        "id": "Q14",
        "dimension": 3,
        "dimension_name": "Readability, Clean Code & Coding Standards",
        "source": "ENVIRONMENT",
        "question": "Does the sample include the sample execution harness lines calling 'execute_sample(__FILE__, __NAMESPACE__, $argv)'?",
        "expected_a": "YES",
        "expected_b": "YES",
        "note_a": "Model A requires sample_helpers.php and invokes execute_sample (patch_a.diff:L162-163).",
        "note_b": "Model B requires sample_helpers.php and invokes execute_sample (patch_b.diff:L144-145)."
    },
    {
        "id": "Q15",
        "dimension": 3,
        "dimension_name": "Readability, Clean Code & Coding Standards",
        "source": "COMMON_ENGINEERING_KNOWLEDGE",
        "question": "Does the implementation declare explicit parameter type hints ('string') and return type ': void' on the function signature?",
        "expected_a": "YES",
        "expected_b": "YES",
        "note_a": "Model A uses string type hints for all parameters and specifies : void return type (patch_a.diff:L60-68).",
        "note_b": "Model B uses string type hints and : void return type (patch_b.diff:L61-70)."
    },
    {
        "id": "Q16",
        "dimension": 3,
        "dimension_name": "Readability, Clean Code & Coding Standards",
        "source": "COMMON_ENGINEERING_KNOWLEDGE",
        "question": "Are the imported classes in the 'use' statements sorted or cleanly grouped without unused imports?",
        "expected_a": "YES",
        "expected_b": "YES",
        "note_a": "Model A cleanly imports DLP V2 Action, Deidentify, BigQueryTable, CloudStorageOptions, FileSet, JobState, etc. (patch_a.diff:L34-46).",
        "note_b": "Model B imports classes cleanly without syntax errors (patch_b.diff:L34-46)."
    },

    # ==========================================
    # DIMENSION 4: Robustness, Error Handling & Defensiveness (8 questions)
    # ==========================================
    {
        "id": "Q17",
        "dimension": 4,
        "dimension_name": "Robustness, Error Handling & Defensiveness",
        "source": "COMMON_ENGINEERING_KNOWLEDGE",
        "question": "Does the sample implement a bounded polling loop with a maximum retry counter or timeout to prevent infinite hanging?",
        "expected_a": "NO",
        "expected_b": "NO",
        "note_a": "Model A uses an unbounded while loop 'while ($job->getState() == JobState::RUNNING || ...)' without an attempt counter, risking an infinite loop (patch_a.diff:L122-126).",
        "note_b": "Model B uses an unbounded while loop 'while (in_array($job->getState(), ...))' without retry limits (patch_b.diff:L109-112)."
    },
    {
        "id": "Q18",
        "dimension": 4,
        "dimension_name": "Robustness, Error Handling & Defensiveness",
        "source": "COMMON_ENGINEERING_KNOWLEDGE",
        "question": "Does the sample close the DLP service client in a finally block to guarantee gRPC/channel cleanup?",
        "expected_a": "NO",
        "expected_b": "YES",
        "note_a": "Model A never calls $dlp->close() anywhere in its function (patch_a.diff).",
        "note_b": "Model B wraps the entire execution in a try-finally block and calls $dlp->close() in finally (patch_b.diff:L137-139)."
    },
    {
        "id": "Q19",
        "dimension": 4,
        "dimension_name": "Robustness, Error Handling & Defensiveness",
        "source": "EXPLICIT_PROMPT",
        "question": "Does the sample inspect and handle non-terminal job states (e.g. FAILED) by reporting job errors?",
        "expected_a": "YES",
        "expected_b": "YES",
        "note_a": "Model A handles JobState::FAILED with a switch case dumping error details (patch_a.diff:L145-151).",
        "note_b": "Model B checks $job->getState() !== JobState::DONE and prints each error message (patch_b.diff:L116-122)."
    },
    {
        "id": "Q20",
        "dimension": 4,
        "dimension_name": "Robustness, Error Handling & Defensiveness",
        "source": "COMMON_ENGINEERING_KNOWLEDGE",
        "question": "Does the sample handle the edge case where the completed job returns zero findings gracefully?",
        "expected_a": "YES",
        "expected_b": "YES",
        "note_a": "Model A checks 'count($infoTypeStats) === 0' and prints 'No findings.' (patch_a.diff:L133-135).",
        "note_b": "Model B checks 'count($infoTypeStats) === 0' and prints 'No findings.' (patch_b.diff:L125-128)."
    },
    {
        "id": "Q21",
        "dimension": 4,
        "dimension_name": "Robustness, Error Handling & Defensiveness",
        "source": "ENVIRONMENT",
        "question": "Does the client instantiation syntax '$dlp = new DlpServiceClient();' precisely match the regex mock substitution used in dlpTest.php?",
        "expected_a": "YES",
        "expected_b": "YES",
        "note_a": "Model A uses '$dlp = new DlpServiceClient();' (patch_a.diff:L70), matching preg_replace('/\\$dlp\\s*=\\s*new\\s+DlpServiceClient\\s*\\(\\s*\\)\\s*;/', 'global $dlp;', $fileContent).",
        "note_b": "Model B uses '$dlp = new DlpServiceClient();' (patch_b.diff:L71), which also matches the regex."
    },
    {
        "id": "Q22",
        "dimension": 4,
        "dimension_name": "Robustness, Error Handling & Defensiveness",
        "source": "COMMON_ENGINEERING_KNOWLEDGE",
        "question": "Does the polling loop include an appropriate sleep interval (between 5 and 30 seconds) to avoid rate-limiting the getDlpJob endpoint?",
        "expected_a": "YES",
        "expected_b": "YES",
        "note_a": "Model A uses sleep(5) on line 124 (patch_a.diff).",
        "note_b": "Model B uses sleep(10) on line 110 (patch_b.diff)."
    },
    {
        "id": "Q23",
        "dimension": 4,
        "dimension_name": "Robustness, Error Handling & Defensiveness",
        "source": "COMMON_ENGINEERING_KNOWLEDGE",
        "question": "Does the sample avoid catching generic exceptions (try-catch Throwable) that would silently suppress fatal runtime errors?",
        "expected_a": "YES",
        "expected_b": "YES",
        "note_a": "Model A does not swallow exceptions with a broad catch (patch_a.diff).",
        "note_b": "Model B uses try-finally without a catch block, preserving uncaught errors (patch_b.diff)."
    },
    {
        "id": "Q24",
        "dimension": 4,
        "dimension_name": "Robustness, Error Handling & Defensiveness",
        "source": "COMMON_ENGINEERING_KNOWLEDGE",
        "question": "Does the sample check whether inspectDetails and result are non-null before accessing getInfoTypeStats?",
        "expected_a": "NO",
        "expected_b": "NO",
        "note_a": "Model A chains directly $job->getInspectDetails()->getResult()->getInfoTypeStats() without null coalescing (patch_a.diff:L132).",
        "note_b": "Model B chains directly $job->getInspectDetails()->getResult()->getInfoTypeStats() without null checks (patch_b.diff:L124)."
    },

    # ==========================================
    # DIMENSION 5: Instruction Following & Scope Discipline (6 questions)
    # ==========================================
    {
        "id": "Q25",
        "dimension": 5,
        "dimension_name": "Instruction Following & Scope Discipline",
        "source": "EXPLICIT_PROMPT",
        "question": "Is the new sample file placed in the exact directory requested ('dlp/src/deidentify_cloud_storage.php')?",
        "expected_a": "YES",
        "expected_b": "YES",
        "note_a": "Model A creates dlp/src/deidentify_cloud_storage.php (patch_a.diff:L1).",
        "note_b": "Model B creates dlp/src/deidentify_cloud_storage.php (patch_b.diff:L1)."
    },
    {
        "id": "Q26",
        "dimension": 5,
        "dimension_name": "Instruction Following & Scope Discipline",
        "source": "EXPLICIT_PROMPT",
        "question": "Does the implementation refrain from modifying existing unrelated sample files in dlp/src/?",
        "expected_a": "YES",
        "expected_b": "YES",
        "note_a": "Model A only touches dlp/src/deidentify_cloud_storage.php; git diff shows 1 file changed (patch_a.diff).",
        "note_b": "Model B only touches dlp/src/deidentify_cloud_storage.php (patch_b.diff)."
    },
    {
        "id": "Q27",
        "dimension": 5,
        "dimension_name": "Instruction Following & Scope Discipline",
        "source": "EXPLICIT_PROMPT",
        "question": "Does the function expose the exact public identifier 'deidentify_cloud_storage' required by Additional Requirements?",
        "expected_a": "YES",
        "expected_b": "YES",
        "note_a": "Model A defines 'function deidentify_cloud_storage' on line 59 (patch_a.diff).",
        "note_b": "Model B defines 'function deidentify_cloud_storage' on line 60 (patch_b.diff)."
    },
    {
        "id": "Q28",
        "dimension": 5,
        "dimension_name": "Instruction Following & Scope Discipline",
        "source": "EXPLICIT_PROMPT",
        "question": "Does the implementation adhere strictly to the requested scope without splitting BigQuery dataset configuration into extraneous unrequested project parameters?",
        "expected_a": "YES",
        "expected_b": "NO",
        "note_a": "Model A accepts $datasetId and $tableId, using $callingProjectId for the BigQuery table (patch_a.diff:L66-67, L88).",
        "note_b": "Model B adds an unrequested '$transformationDetailsTableProjectId' parameter, breaking contract scope (patch_b.diff:L67)."
    },
    {
        "id": "Q29",
        "dimension": 5,
        "dimension_name": "Instruction Following & Scope Discipline",
        "source": "EXPLICIT_PROMPT",
        "question": "Does the sample output the job name upon completion as explicitly required by the prompt?",
        "expected_a": "YES",
        "expected_b": "YES",
        "note_a": "Model A prints printf('Job %s status: ...', $job->getName()) on patch_a.diff:L129.",
        "note_b": "Model B prints printf('Job name: %s', $job->getName()) on patch_b.diff:L114."
    },
    {
        "id": "Q30",
        "dimension": 5,
        "dimension_name": "Instruction Following & Scope Discipline",
        "source": "EXPLICIT_PROMPT",
        "question": "Does the implementation refrain from adding unrequested CLI interactive prompts or readline calls?",
        "expected_a": "YES",
        "expected_b": "YES",
        "note_a": "Model A does not use readline or interactive prompts (patch_a.diff).",
        "note_b": "Model B does not use interactive prompts (patch_b.diff)."
    },

    # ==========================================
    # DIMENSION 6: Planning, Research & Exploration (6 questions)
    # ==========================================
    {
        "id": "Q31",
        "dimension": 6,
        "dimension_name": "Planning, Research & Exploration",
        "source": "COMMON_ENGINEERING_KNOWLEDGE",
        "question": "Did the agent inspect existing DLP samples in dlp/src/ to determine naming conventions and SDK usage patterns before authoring?",
        "expected_a": "YES",
        "expected_b": "YES",
        "note_a": "Model A read existing samples like deidentify_dates.php, inspect_bigquery.php, and create_inspect_template.php in Steps 26-41.",
        "note_b": "Model B examined dlp repository structure and samples in Steps 3-7."
    },
    {
        "id": "Q32",
        "dimension": 6,
        "dimension_name": "Planning, Research & Exploration",
        "source": "ENVIRONMENT",
        "question": "Did the agent inspect the existing test suite in dlp/test/dlpTest.php to understand how samples are invoked and tested in this repository?",
        "expected_a": "YES",
        "expected_b": "NO",
        "note_a": "Model A viewed /workspace/repo/dlp/test/dlpTest.php in Step 53.",
        "note_b": "Model B attempted to read test files in incorrect directories and never inspected dlpTest.php (Steps 10-12)."
    },
    {
        "id": "Q33",
        "dimension": 6,
        "dimension_name": "Planning, Research & Exploration",
        "source": "COMMON_ENGINEERING_KNOWLEDGE",
        "question": "Did the agent demonstrate effective navigation without repeatedly failing commands due to invalid working directories?",
        "expected_a": "YES",
        "expected_b": "NO",
        "note_a": "Model A operated smoothly in /workspace/repo without directory navigation failures.",
        "note_b": "Model B suffered repeated path failures looking for /filesystem and /workspace in Steps 11, 12, and 32."
    },
    {
        "id": "Q34",
        "dimension": 6,
        "dimension_name": "Planning, Research & Exploration",
        "source": "COMMON_ENGINEERING_KNOWLEDGE",
        "question": "Did the agent inspect protobuf class definitions or methods for DLP JobState to use canonical enum constants?",
        "expected_a": "YES",
        "expected_b": "YES",
        "note_a": "Model A inspected JobState constants in Step 39 (JobState::DONE, JobState::RUNNING).",
        "note_b": "Model B referenced JobState enum constants correctly."
    },
    {
        "id": "Q35",
        "dimension": 6,
        "dimension_name": "Planning, Research & Exploration",
        "source": "COMMON_ENGINEERING_KNOWLEDGE",
        "question": "Did the agent verify sample execution helpers in testing/sample_helpers.php before including them in the snippet?",
        "expected_a": "YES",
        "expected_b": "NO",
        "note_a": "Model A inspected /workspace/repo/testing/sample_helpers.php in Step 29.",
        "note_b": "Model B included sample_helpers.php based on convention without inspecting its implementation."
    },
    {
        "id": "Q36",
        "dimension": 6,
        "dimension_name": "Planning, Research & Exploration",
        "source": "COMMON_ENGINEERING_KNOWLEDGE",
        "question": "Did the agent inspect the golden patch or test patch if available in the task bundle rather than guessing parameter conventions?",
        "expected_a": "NO",
        "expected_b": "YES",
        "note_a": "Model A deduced the solution entirely from codebase context without reading bundle/golden.patch.",
        "note_b": "Model B read bundle/golden.patch in Step 17 and Step 29, but ironically still deviated on parameters."
    },

    # ==========================================
    # DIMENSION 7: Verification & Testing Rigor (6 questions)
    # ==========================================
    {
        "id": "Q37",
        "dimension": 7,
        "dimension_name": "Verification & Testing Rigor",
        "source": "ENVIRONMENT",
        "question": "Did the agent run a PHP syntax linter ('php -l') on the authored sample to verify zero syntax errors?",
        "expected_a": "YES",
        "expected_b": "YES",
        "note_a": "Model A executed 'php -l' in Step 50: 'No syntax errors detected in /workspace/repo/dlp/src/deidentify_cloud_storage.php'.",
        "note_b": "Model B claims PHP syntax check passed in final answer after checking in Step 34."
    },
    {
        "id": "Q38",
        "dimension": 7,
        "dimension_name": "Verification & Testing Rigor",
        "source": "ENVIRONMENT",
        "question": "Did the agent execute the test suite (e.g. PHPUnit or test runner) to validate the implementation during its trajectory?",
        "expected_a": "YES",
        "expected_b": "NO",
        "note_a": "Model A executed phpunit in Step 54 to verify the suite and test execution.",
        "note_b": "Model B failed to locate phpunit and did not execute any tests (Step 38 report)."
    },
    {
        "id": "Q39",
        "dimension": 7,
        "dimension_name": "Verification & Testing Rigor",
        "source": "COMMON_ENGINEERING_KNOWLEDGE",
        "question": "Did the agent verify function existence and parameter reflection using a standalone PHP one-liner?",
        "expected_a": "YES",
        "expected_b": "NO",
        "note_a": "Model A ran reflection in Step 55: 'Function exists: Google\\Cloud\\Samples\\Dlp\\deidentify_cloud_storage Parameters count: 8'.",
        "note_b": "Model B did not verify reflection or parameter count with a CLI script."
    },
    {
        "id": "Q40",
        "dimension": 7,
        "dimension_name": "Verification & Testing Rigor",
        "source": "ENVIRONMENT",
        "question": "Did the agent run code style checks (e.g. PHP CS Fixer) on the modified code?",
        "expected_a": "NO",
        "expected_b": "YES",
        "note_a": "Model A inspected run_cs_check.sh in Step 46 but did not run php-cs-fixer against the new file.",
        "note_b": "Model B ran PHP CS Fixer dry run and reported compliance in its final answer."
    },
    {
        "id": "Q41",
        "dimension": 7,
        "dimension_name": "Verification & Testing Rigor",
        "source": "COMMON_ENGINEERING_KNOWLEDGE",
        "question": "Did the agent verify Git status before submitting to confirm only the expected new sample file was staged/untracked?",
        "expected_a": "YES",
        "expected_b": "NO",
        "note_a": "Model A ran 'git status' in Step 56 and Step 58 confirming only dlp/src/deidentify_cloud_storage.php was untracked.",
        "note_b": "Model B did not check git status in /workspace/repo."
    },
    {
        "id": "Q42",
        "dimension": 7,
        "dimension_name": "Verification & Testing Rigor",
        "source": "COMMON_ENGINEERING_KNOWLEDGE",
        "question": "Did the agent test CLI usage of the script by invoking it with insufficient arguments to verify the usage message?",
        "expected_a": "YES",
        "expected_b": "NO",
        "note_a": "Model A invoked php dlp/src/deidentify_cloud_storage.php in Step 52 and verified the usage output string.",
        "note_b": "Model B did not test CLI execution."
    },

    # ==========================================
    # DIMENSION 8: Communication & Explanation Quality (4 questions)
    # ==========================================
    {
        "id": "Q43",
        "dimension": 8,
        "dimension_name": "Communication & Explanation Quality",
        "source": "COMMON_ENGINEERING_KNOWLEDGE",
        "question": "Does the final response clearly state the exact path of the newly created sample file?",
        "expected_a": "YES",
        "expected_b": "YES",
        "note_a": "Model A explicitly cites 'dlp/src/deidentify_cloud_storage.php' in the opening sentence of final_answer_a.txt.",
        "note_b": "Model B explicitly cites 'dlp/src/deidentify_cloud_storage.php' on line 1 of final_answer_b.txt."
    },
    {
        "id": "Q44",
        "dimension": 8,
        "dimension_name": "Communication & Explanation Quality",
        "source": "COMMON_ENGINEERING_KNOWLEDGE",
        "question": "Does the final response clearly describe the key workflow components (GCS input/output, templates, BigQuery, polling, summary)?",
        "expected_a": "YES",
        "expected_b": "YES",
        "note_a": "Model A organizes bullet points covering Configuration, Job Submission & Polling, and Summary Reporting (final_answer_a.txt).",
        "note_b": "Model B lists all bullet points covering input, output, templates, BigQuery, polling, and errors (final_answer_b.txt)."
    },
    {
        "id": "Q45",
        "dimension": 8,
        "dimension_name": "Communication & Explanation Quality",
        "source": "COMMON_ENGINEERING_KNOWLEDGE",
        "question": "Does the final response avoid verbose conversational filler or flattery, maintaining a professional technical tone?",
        "expected_a": "YES",
        "expected_b": "YES",
        "note_a": "Model A's final answer is concise (662 characters) and purely technical.",
        "note_b": "Model B's final answer is concise (863 characters) and structured."
    },
    {
        "id": "Q46",
        "dimension": 8,
        "dimension_name": "Communication & Explanation Quality",
        "source": "COMMON_ENGINEERING_KNOWLEDGE",
        "question": "Does the agent explain during execution why it takes non-trivial actions rather than remaining completely silent for 20+ turns?",
        "expected_a": "YES",
        "expected_b": "YES",
        "note_a": "Model A provides intermediate commentary across its exploration steps.",
        "note_b": "Model B documents its reasoning as it navigates the bundle."
    },

    # ==========================================
    # DIMENSION 9: Summary & Deliverable Precision (4 questions)
    # ==========================================
    {
        "id": "Q47",
        "dimension": 9,
        "dimension_name": "Summary & Deliverable Precision",
        "source": "COMMON_ENGINEERING_KNOWLEDGE",
        "question": "Is the final summary completely truthful about verification results without falsely claiming that unit tests passed if they did not run?",
        "expected_a": "YES",
        "expected_b": "YES",
        "note_a": "Model A does not falsely claim full unit test pass; it reports the factual components implemented.",
        "note_b": "Model B honestly notes: 'Full PHPUnit execution was unavailable because vendor/bin/phpunit is not installed' (final_answer_b.txt:L24)."
    },
    {
        "id": "Q48",
        "dimension": 9,
        "dimension_name": "Summary & Deliverable Precision",
        "source": "COMMON_ENGINEERING_KNOWLEDGE",
        "question": "Does the final deliverable include the exact public function name and signature details without omitting required parameter names?",
        "expected_a": "YES",
        "expected_b": "NO",
        "note_a": "Model A names deidentify_cloud_storage and details all configured parameters accurately.",
        "note_b": "Model B writes 'deidentify_cloud_storage(...)' hiding its broken 9-parameter signature (final_answer_b.txt:L5)."
    },
    {
        "id": "Q49",
        "dimension": 9,
        "dimension_name": "Summary & Deliverable Precision",
        "source": "COMMON_ENGINEERING_KNOWLEDGE",
        "question": "Does the summary accurately document that structured data transformation includes CSV file types?",
        "expected_a": "YES",
        "expected_b": "NO",
        "note_a": "Model A explicitly highlights 'structured data (CSV)' in final_answer_a.txt:L4, matching its code patch_a.diff:L102.",
        "note_b": "Model B claims it configured structured content, but completely omitted FileType::CSV in code (patch_b.diff)."
    },
    {
        "id": "Q50",
        "dimension": 9,
        "dimension_name": "Summary & Deliverable Precision",
        "source": "COMMON_ENGINEERING_KNOWLEDGE",
        "question": "Are all files listed in the final deliverable summary actually created in the Git patch without phantom files?",
        "expected_a": "YES",
        "expected_b": "YES",
        "note_a": "Model A only claims and delivers dlp/src/deidentify_cloud_storage.php (patch_a.diff).",
        "note_b": "Model B only claims and delivers dlp/src/deidentify_cloud_storage.php (patch_b.diff)."
    }
]

print(f"Total questions authored: {len(questions)}")
# Count by dimension
dim_counts = {}
for q in questions:
    d = q['dimension']
    dim_counts[d] = dim_counts.get(d, 0) + 1
for d in sorted(dim_counts.keys()):
    print(f"Dimension {d}: {dim_counts[d]} questions")

# Count expected answers for Model A and Model B
a_yes = sum(1 for q in questions if q['expected_a'] == 'YES')
b_yes = sum(1 for q in questions if q['expected_b'] == 'YES')
print(f"Overall Question Bank A: {a_yes}/50 YES ({a_yes/50*100:.1f}%), B: {b_yes}/50 YES ({b_yes/50*100:.1f}%)")

with open('question_bank_50.json', 'w', encoding='utf-8') as f:
    json.dump(questions, f, indent=2, ensure_ascii=False)
print("Saved question_bank_50.json")
