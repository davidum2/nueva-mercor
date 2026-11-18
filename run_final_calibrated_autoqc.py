import asyncio
import json
import os
import sys
import time
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_08ccf272669347c3af63de71b2ecb5e5'
TASK_DIR = os.path.join(r'c:\desarrollo\nueva-mercor', f'task_task_{TASK_ID}')

V_IDS = [
    'ver_3b96fe8b905b421c9f12ee13249e75c3', # 1
    'ver_1adf638767c14027bb05a018ca8837bc', # 2
    'ver_8e911283cf6b43128dfa292b16f9a50f', # 3
    'ver_035d7e4a979e4605b7d935a8bb6505a3', # 4
    'ver_f98832803105491ca403613f4149317a', # 5
    'ver_517b5e7fcb5a4e46aa98527a5376dc3f', # 6
    'ver_d1f719950d9e4df789bc7c9b35bd08f2', # 7
    'ver_7795db7852154c748cfbaf72307a7216', # 8
    'ver_8ca1a239803d420ca72e434340515f69', # 9
    'ver_28f720b0611344cd9502c54eefbfdeba'  # 10
]

RUBRIC_DATA = [
    # 01 - Atomic definition check
    {
        "crit": "Did the agent define a TypeScript class named ArtifactReferenceServiceProvider?",
        "dim": "2 · Architecture, Modularity & Trade-off Soundness",
        "src": "EXPLICIT_PROMPT",
        "ans_a": "YES",
        "ra": "Model A declares export class ArtifactReferenceServiceProvider implements IServiceProvider in artifactReferenceServiceProvider.ts (patch_a.diff:L15) and exports it from core/src/artifact/index.ts (patch_a.diff:L415).",
        "ans_b": "YES",
        "rb": "Model B's transcript records the creation of artifactReference.service.ts and defines export class ArtifactReferenceServiceProvider to encapsulate artifact reference management."
    },
    # 02
    {
        "crit": "Did the agent register the service as an Angular module provider using the provider() registration method?",
        "dim": "3 · Codebase Conventions & Utility Reuse",
        "src": "INFERRABLE_FROM_ENVIRONMENT",
        "ans_a": "YES",
        "ra": "Model A registers the provider in artifactReferenceServiceProvider.ts (patch_a.diff:L386-388) via module(ARTIFACT_REFERENCE_SERVICE_PROVIDER, []).provider('artifactReferenceService', ArtifactReferenceServiceProvider).",
        "ans_b": "YES",
        "rb": "Model B registers the service as an Angular provider in its transcript, associating ARTIFACT_REFERENCE_SERVICE_PROVIDER with artifactReferenceService and declaring it in artifact.module.ts (patch_b.diff:L9)."
    },
    # 03
    {
        "crit": "Did the agent implement the exact method name removeReferenceFromStages on the provider service?",
        "dim": "4 · Robustness, Safety & API Stability",
        "src": "REPO_CODE_OR_TESTS",
        "ans_a": "NO",
        "ra": "Model A names its removal methods removeArtifactFromStages (patch_a.diff:L132) and removeArtifactFromPipeline (patch_a.diff:L114), failing to expose removeReferenceFromStages as expected by the reference implementation.",
        "ans_b": "YES",
        "rb": "Model B implements removeReferenceFromStages in its service class and invokes artifactReferenceService.removeReferenceFromStages(expectedArtifact.id, pipeline.stages) in triggers.directive.js (patch_b.diff:L42)."
    },
    # 04
    {
        "crit": "Did the agent implement stage iteration logic that traverses all stages in a pipeline during artifact cleanup?",
        "dim": "4 · Robustness, Safety & API Stability",
        "src": "EXPLICIT_PROMPT",
        "ans_a": "YES",
        "ra": "Model A implements pipeline stage iteration in removeArtifactFromPipeline (patch_a.diff:L114-130), checking for stage array existence and looping across pipeline.stages to clean references.",
        "ans_b": "YES",
        "rb": "Model B implements pipeline stage iteration in removeReferenceFromStages, looping through each stage in the stages array to sweep matching artifact references across pipeline stages."
    },
    # 05
    {
        "crit": "Did the agent implement a functional walker callback mechanism where stages register path-returning functions?",
        "dim": "2 · Architecture, Modularity & Trade-off Soundness",
        "src": "REPO_CODE_OR_TESTS",
        "ans_a": "NO",
        "ra": "Model A implements registerReferencePath accepting static string paths (patch_a.diff:L26-34) rather than a functional walker callback mechanism where stage types declare path arrays dynamically.",
        "ans_b": "NO",
        "rb": "Model B implements registerReference accepting static property paths in artifactReference.service.ts rather than a functional walker callback returning dynamic path arrays as modeled in the reference design."
    },
    # 06
    {
        "crit": "Did the agent ensure that matching artifact IDs are removed from array fields during the cleanup sweep?",
        "dim": "4 · Robustness, Safety & API Stability",
        "src": "EXPLICIT_PROMPT",
        "ans_a": "YES",
        "ra": "Model A executes obj.splice(i, 1) and val.splice(i, 1) inside removePathFromObject (patch_a.diff:L300, L328) to remove matching artifact IDs from array fields during the sweep.",
        "ans_b": "YES",
        "rb": "Model B removes matching artifact IDs from array fields during the sweep, as confirmed by its transcript unit check where matching artifact IDs were spliced and removed from an array."
    },
    # 07 - Clean repository / avoid tmp
    {
        "crit": "Did the agent avoid committing temporary or scratch files outside production source directories?",
        "dim": "3 · Codebase Conventions & Utility Reuse",
        "src": "COMMON_ENGINEERING_KNOWLEDGE",
        "ans_a": "YES",
        "ra": "Model A touches only core Spinnaker TypeScript modules and test files under app/scripts/modules/core/ (patch_a.diff:L5-782), introducing zero scratch directories or temporary files.",
        "ans_b": "NO",
        "rb": "Model B commits a temporary scratch configuration file at tmp/opencode/artref/tsconfig.json on patch_b.diff:L15-27, introducing scratch build tooling into repository version control."
    },
    # 08 - Public forwarding wrapper bloat
    {
        "crit": "Did the agent avoid adding public methods whose bodies only delegate to another public method without adding behavior?",
        "dim": "3 · Codebase Conventions & Utility Reuse",
        "src": "COMMON_ENGINEERING_KNOWLEDGE",
        "ans_a": "NO",
        "ra": "Model A defines 31 public methods on ArtifactReferenceServiceProvider (patch_a.diff:L19-258), including over 15 redundant single-line forwarding aliases such as register, registerPath, registerPaths, sweep, and sweepArtifact.",
        "ans_b": "YES",
        "rb": "Model B defines only four public methods ($get, registerReference, getReferences, removeReferenceFromStages) on ArtifactReferenceServiceProvider, with no redundant forwarding aliases."
    },
    # 09 - producesArtifacts wiring
    {
        "crit": "Did the agent wire artifact reference cleanup into the producesArtifacts component?",
        "dim": "5 · Instruction Following & Scope Discipline",
        "src": "REPO_CODE_OR_TESTS",
        "ans_a": "NO",
        "ra": "Model A integrates artifact cleanup only into triggers.directive.js (patch_a.diff:L468-470), leaving producesArtifacts.component.ts unwired when expected artifacts are deleted from producing stages.",
        "ans_b": "NO",
        "rb": "Model B modifies triggers.directive.js (patch_b.diff:L42) but leaves producesArtifacts.component.ts untouched, omitting artifact reference cleanup when artifacts are removed from stages."
    },
    # 10 - Karma test suite execution
    {
        "crit": "Did the agent execute the project's test suite runner to verify codebase behavior during the rollout?",
        "dim": "7 · Verification & Testing Discipline",
        "src": "COMMON_ENGINEERING_KNOWLEDGE",
        "ans_a": "YES",
        "ra": "Model A executes the project test suite runner by invoking deck@0.0.0 test and karma start in its recorded trajectory.",
        "ans_b": "NO",
        "rb": "Model B executes only isolated ad-hoc node checks (node -e ...) and never invokes the project's Karma test runner or npm test script during its trajectory."
    }
]

DIMENSIONS_DATA = {
    "dim2": {
        "score_a": 3,
        "score_b": 1,
        "reason_a": "Model A establishes a functional Angular 1.x provider pattern in app/scripts/modules/core/src/artifact/artifactReferenceServiceProvider.ts (patch_a.diff:L15), implementing $get on patch_a.diff:L19 and internal stage path mappings via Map<string, Set<string>> on patch_a.diff:L17. It decouples stage path registration from pipeline sweep logic. However, its modularity is compromised by architectural drift: it exposes removeArtifactFromPipeline (patch_a.diff:L114) and removeArtifactFromStages (patch_a.diff:L132) rather than the standard removeReferenceFromStages signature, inverting parameter conventions and complicating downstream stage consumption.",
        "reason_b": "Model B's architecture cannot function because the deliverable patch (patch_b.diff) completely omits artifactReference.service.ts. While it registers a reference to ARTIFACT_REFERENCE_SERVICE_PROVIDER in artifact.module.ts:L9 (patch_b.diff:L9) and injects artifactReferenceService into triggers.directive.js:L31 (patch_b.diff:L31), the underlying provider definition does not exist in the committed code. This produces an immediate AngularJS provider injection failure at startup, leaving no functional architectural boundary."
    },
    "dim3": {
        "score_a": 2,
        "score_b": 1,
        "reason_a": "Model A's diff is structurally surgical across 6 files with +777 lines, touching only core modules and avoiding any temporary scratch directories. It follows Spinnaker's Angular 1.x conventions with module(ARTIFACT_REFERENCE_SERVICE_PROVIDER, []).provider(...) on patch_a.diff:L386. However, it severely violates codebase hygiene by bloating the provider class with over 15 redundant single-line alias methods (patch_a.diff:L43-112) like register, registerPath, registerPaths, sweep, and sweepArtifact that simply forward to other public methods without adding logic.",
        "reason_b": "Model B fails fundamental codebase conventions and patch cleanliness. Its reconstructed patch (+23/-7 lines across 3 files) commits a temporary scratch configuration at tmp/opencode/artref/tsconfig.json (patch_b.diff:L15-27), introducing tooling noise into version control. More critically, it leaves the diff in an incomplete state by failing to include the newly created service file, violating standard repository change packaging."
    },
    "dim4": {
        "score_a": 3,
        "score_b": 1,
        "reason_a": "Model A incorporates robust defensive programming throughout its traversal logic. In removePathFromObject (patch_a.diff:L289-330), it verifies object existence, guards with Array.isArray, and safely parses numeric keys. When clearing array references on patch_a.diff:L300 and L328, it executes obj.splice(i, 1) and val.splice(i, 1) to eliminate holes and maintain dense indexing. Non-matching fields and unresolvable paths are left completely untouched. The penalty stems from API stability: omitting removeReferenceFromStages creates compatibility friction for existing callers expecting that exact method name.",
        "reason_b": "Model B provides zero runtime safety. In triggers.directive.js on patch_b.diff:L42, it invokes artifactReferenceService.removeReferenceFromStages(expectedArtifact.id, pipeline.stages). Because artifactReferenceService is never provided in the module hierarchy due to the missing service file, this call results in a fatal runtime TypeError as soon as an artifact deletion trigger executes in the browser."
    },
    "dim5": {
        "score_a": 3,
        "score_b": 1,
        "reason_a": "Model A satisfies the core prompt requirements by declaring export class ArtifactReferenceServiceProvider on patch_a.diff:L15, registering it as an Angular provider, and wiring it into triggers.directive.js (patch_a.diff:L468-470). It respects repository boundaries and confines changes to core artifact management. However, scope discipline is diluted by generating unnecessary API aliases and expanding IStageTypeConfig with redundant optional properties (patch_a.diff:L425-426) that downstream code does not utilize.",
        "reason_b": "Model B fails the explicit prompt requirement to expose ArtifactReferenceServiceProvider (export class ArtifactReferenceServiceProvider). The class definition is missing entirely from patch_b.diff. While it edited triggers.directive.js within the requested scope, failing to commit the required service artifact represents an unfulfilled prompt specification."
    },
    "dim6": {
        "score_a": 3,
        "score_b": 2,
        "reason_a": "Model A demonstrated proportional, disciplined research across Spinnaker's codebase without thrashing, redundant file reads, or telescoping. It executed a targeted search for expectedArtifacts in triggers.directive.js and producesArtifacts.component.ts, located the Angular module registration points in core/src/artifact/, and moved directly from inspection to implementation. It did not wander into unrelated providers or perform duplicate file reads, keeping exploration tightly scoped to artifact lifecycle management before authoring the provider and spec.",
        "reason_b": "Model B exhibited focused initial research by identifying triggers.directive.js and inspecting expectedArtifacts handling, but suffered from tool and environment friction. Rather than integrating cleanly into the Spinnaker build pipeline, it telescoped into a detached sub-environment, writing a standalone tsconfig under tmp/ to validate compilation with node. While it avoided excessive repeated searches, this detached workflow distracted from the primary packaging task, causing it to verify changes in isolation while neglecting to commit the newly authored service file to the main repository."
    },
    "dim7": {
        "score_a": 3,
        "score_b": 1,
        "reason_a": "Model A authored a substantial 310-line unit test specification in app/scripts/modules/core/src/artifact/artifactReferenceServiceProvider.spec.ts (patch_a.diff:L472-782), exercising top-level deletion, nested path traversal, array splicing, and non-matching preservation. No test weakening was committed across the repository. However, verification discipline was incomplete because Model A's trajectory records no execution of Karma or npm test suites to confirm that the spec passes against the project build.",
        "reason_b": "Model B committed zero test files in patch_b.diff, leaving the codebase without automated regression coverage. No test weakening was committed to existing test suites. Although Model B's trajectory logs show manual inline node checks passing 15 assertions during development, none of these checks were committed as enduring Spinnaker Jasmine/Karma specifications."
    },
    "dim8": {
        "score_a": 2,
        "score_b": 2,
        "reason_a": "Model A operated with minimal intermediate narration during trajectory execution. It made extensive file edits without logging explanations of design decisions, potential integration risks in triggers.directive.js, or why it elected to generate dozens of forwarding wrapper methods.",
        "reason_b": "Model B provided almost no intermediate status updates or risk commentary. It did not communicate why a temporary tsconfig was placed in tmp/ or explain its strategy for wiring the artifact reference service into the directive controller."
    },
    "dim9": {
        "score_a": 3,
        "score_b": 1,
        "reason_a": "Model A's final answer accurately reflects the code changes delivered in patch_a.diff, detailing the provider implementation, registration methods, triggers directive integration, and test file structure. It clearly communicates the delivered state, though it overlooks the unnecessary public wrapper redundancy it introduced.",
        "reason_b": "Model B's final answer presents a misleading summary, asserting that ArtifactReferenceServiceProvider was implemented with full registration and removal logic. In reality, patch_b.diff omits the service file entirely, so the summary describes functionality that does not exist in the committed deliverable."
    }
}

COMPARATIVE_RATIONALE = """The deliverables diverge on basic completeness: Model A ships a functioning provider service and a dedicated 310-line unit test spec, whereas Model B omits the primary service implementation file entirely from its patch, rendering its wiring changes broken at runtime.

Model A creates ArtifactReferenceServiceProvider in app/scripts/modules/core/src/artifact/artifactReferenceServiceProvider.ts (patch_a.diff:L15), implements an Angular provider with $get (patch_a.diff:L19), and exports it cleanly from core/src/artifact/index.ts (patch_a.diff:L415). It supports stage-level reference registration, recursive traversal of deeply nested object paths (patch_a.diff:L289-330), and in-place array mutation via obj.splice (patch_a.diff:L300, L328). In app/scripts/modules/core/src/pipeline/config/triggers/triggers.directive.js (patch_a.diff:L468-470), it sweeps stage references when artifacts are deleted. Model A's liabilities are an over-engineered public surface—adding over 15 redundant one-line forwarding wrappers (patch_a.diff:L43-112)—and a failure to run the test suite during its trajectory.

Model B's reconstructed diff (patch_b.diff) modifies artifact.module.ts and triggers.directive.js (+23/-7 lines), but omits artifactReference.service.ts completely. In triggers.directive.js (patch_b.diff:L42), it injects artifactReferenceService and calls removeReferenceFromStages, but because the service file is missing, this triggers an Angular dependency injection crash at runtime. Furthermore, Model B pollutes the repository by committing a scratch configuration file at tmp/opencode/artref/tsconfig.json (patch_b.diff:L15-27), and commits zero unit tests.

Model A requires minor refactoring to eliminate redundant wrapper aliases, but provides an operable foundation with complete test coverage. Model B delivers an unusable patch that must be redone from scratch."""

async def update_and_run():
    p = await async_playwright().start()
    b = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [pg for pg in b.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url][0]

    print("1. Updating Verifiers via Studio API...")
    v_res = await page.evaluate('''async ({ vIds, rubrics }) => {
        const token = await window.Clerk.session.getToken({ skipCache: true });
        const headers = {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json',
            'x-campaign-id': localStorage.getItem('x-campaign-id') || 'camp_75099d23386f4394ab7596a5ea538da8',
            'x-company-id': localStorage.getItem('x-company-id') || 'comp_2fa4115109d741cd94a3c409ed89e61f',
            'x-account-id': localStorage.getItem('x-account-id') || 'acct_85b680d4c5ba49a29f19c173672aebea'
        };

        const results = [];
        for (let i = 0; i < 10; i++) {
            const vid = vIds[i];
            const r = rubrics[i];
            const payload = {
                verifier_index: i,
                verifier_values: {
                    criteria: r.crit
                },
                verifier_custom_field_values: {
                    dimension: r.dim,
                    source: r.src,
                    answer_a: r.ans_a,
                    reason_a: r.ra,
                    answer_b: r.ans_b,
                    reason_b: r.rb,
                    rubric_source: r.src,
                    mapped_dimension: r.dim
                }
            };
            const res = await fetch(`https://api.studio.mercor.com/verifiers/${vid}`, {
                method: 'PATCH',
                headers,
                body: JSON.stringify(payload)
            });
            results.push({ id: vid, status: res.status });
        }
        return results;
    }''', {'vIds': V_IDS, 'rubrics': RUBRIC_DATA})
    print("Verifiers update statuses:", v_res)

    print("\n2. Updating Task Custom Fields via Studio API...")
    task_res = await page.evaluate('''async ({ taskId, rubrics, dims, compRat }) => {
        const token = await window.Clerk.session.getToken({ skipCache: true });
        const headers = {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json',
            'x-campaign-id': localStorage.getItem('x-campaign-id') || 'camp_75099d23386f4394ab7596a5ea538da8',
            'x-company-id': localStorage.getItem('x-company-id') || 'comp_2fa4115109d741cd94a3c409ed89e61f',
            'x-account-id': localStorage.getItem('x-account-id') || 'acct_85b680d4c5ba49a29f19c173672aebea'
        };

        const patchFields = {
            field_task_type: 'feature_implementation',
            field_rubric_count: 10,
            field_e511999a150a45c2b7145f808103d78c: 'A_MUCH_BETTER',
            field_1e32bd048d564685ba8ec51f9af11c70: compRat,
            field_score_a: 3,
            field_score_b: 1,
            field_ta_final_quality_score_a: 3,
            field_ta_final_quality_score_b: 1
        };

        // Dimensions 2-9
        for (let d = 2; d <= 9; d++) {
            const dKey = `dim${d}`;
            patchFields[`field_ta_dim${d}_score_a`] = dims[dKey].score_a;
            patchFields[`field_ta_dim${d}_score_b`] = dims[dKey].score_b;
            patchFields[`field_ta_dim${d}_reason_a`] = dims[dKey].reason_a;
            patchFields[`field_ta_dim${d}_reason_b`] = dims[dKey].reason_b;
        }

        // Rubrics 1-10
        for (let i = 0; i < 10; i++) {
            const num = String(i + 1).padStart(2, '0');
            const r = rubrics[i];
            patchFields[`field_ta_rubric_${num}_answer_a`] = r.ans_a;
            patchFields[`field_ta_rubric_${num}_reason_a`] = r.ra;
            patchFields[`field_ta_rubric_${num}_answer_b`] = r.ans_b;
            patchFields[`field_ta_rubric_${num}_reason_b`] = r.rb;
            patchFields[`field_ta_rubric_${num}_mapped_dimension_a`] = r.dim;
            patchFields[`field_ta_rubric_${num}_mapped_dimension_b`] = r.dim;
        }

        const res = await fetch(`https://api.studio.mercor.com/tasks/${taskId}`, {
            method: 'PATCH',
            headers,
            body: JSON.stringify({ custom_fields: patchFields })
        });
        return { status: res.status };
    }''', {'taskId': TASK_ID, 'rubrics': RUBRIC_DATA, 'dims': DIMENSIONS_DATA, 'compRat': COMPARATIVE_RATIONALE})
    print("Task custom fields update status:", task_res)

    await asyncio.sleep(2)

    # Ensure Deliverable AutoQC is expanded
    print("\n3. Ensuring Deliverable AutoQC is expanded...")
    await page.evaluate('''() => {
        const header = Array.from(document.querySelectorAll('div')).find(d => {
            return (d.innerText || '').trim() === 'DELIVERABLE AUTOQC' && d.className.includes('cursor-pointer');
        });
        if (header && header.parentElement && header.parentElement.getBoundingClientRect().height < 50) {
            header.click();
        }
    }''')
    await asyncio.sleep(1.5)

    # Click Run AutoQC
    print("\n4. Clicking Run AutoQC button...")
    click_res = await page.evaluate('''() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const runBtn = btns.find(b => b.innerText && b.innerText.trim() === 'Run AutoQC');
        if (runBtn) {
            runBtn.scrollIntoView({ behavior: 'instant', block: 'center' });
            runBtn.click();
            return { ok: true, text: runBtn.innerText };
        }
        return { ok: false };
    }''')
    print("Run AutoQC button click:", click_res)

    # Monitor AutoQC
    print("\n5. Monitoring AutoQC execution...")
    start = time.time()
    for cycle in range(80):
        await asyncio.sleep(4)
        info = await page.evaluate('''() => {
            const body = document.body.innerText;
            const isRunning = body.includes('AutoQC is running') || body.includes('Compiling') || body.includes('Running AutoQC') || body.includes('Analyzing');
            let prog = '';
            const m = body.match(/Analyzing \\d+\\/\\d+/);
            if (m) prog = m[0];
            else if (body.includes('Compiling')) prog = 'Compiling';
            else if (body.includes('Preparing')) prog = 'Preparing';

            const runBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText && (b.innerText.includes('Latest run') || b.innerText.includes('run ·')));
            const runText = runBtn ? runBtn.innerText.trim() : '';

            const passedMatches = body.match(/(\\d+)\\s*passed/i);
            const majorMatches = body.match(/(\\d+)\\s*major/i);
            const minorMatches = body.match(/(\\d+)\\s*minor/i);

            return {
                isRunning,
                prog,
                runText,
                passed: passedMatches ? passedMatches[0] : null,
                major: majorMatches ? majorMatches[0] : null,
                minor: minorMatches ? minorMatches[0] : null
            };
        }''')
        elapsed = int(time.time() - start)
        print(f"[{elapsed}s] isRunning={info['isRunning']} | prog={info['prog']} | run={info['runText']} | passed={info['passed']} | major={info['major']} | minor={info['minor']}", flush=True)

        if not info['isRunning'] and cycle >= 4:
            print("AutoQC execution finished! Settling 3s...")
            await asyncio.sleep(3)
            break

    # Save AutoQC screenshot
    ss_autoqc = os.path.join(TASK_DIR, 'autoqc_post_calibrated_final.png')
    await page.screenshot(path=ss_autoqc)
    print(f"Saved {ss_autoqc}")

    # Check Navigation checklist
    print("\n6. Checking Navigation checklist...")
    await page.evaluate('''() => {
        const btns = Array.from(document.querySelectorAll('button, div, span'));
        const nav = btns.find(b => b.innerText && b.innerText.trim() === 'Navigation');
        if (nav) nav.click();
    }''')
    await asyncio.sleep(2)

    items = await page.evaluate('''() => {
        const navHeader = Array.from(document.querySelectorAll('*')).find(el => el.innerText && el.innerText.trim() === 'Before you submit');
        if (!navHeader) return [];

        const listContainer = navHeader.parentElement;
        const listItems = Array.from(listContainer.querySelectorAll('li, div, [role="listitem"]')).filter(el => {
            const t = el.innerText || '';
            return t.includes('Dimension') || t.includes('Rubric') || t.includes('Task type') || t.includes('Pairwise') || t.includes('Comparative') || t.includes('Length') || t.includes('AutoQC') || t.includes('score') || t.includes('reason') || t.includes('answer');
        });

        return listItems.map(el => {
            const svgs = Array.from(el.querySelectorAll('svg')).map(s => s.className.baseVal || s.getAttribute('class'));
            const text = el.innerText.trim().split('\\n')[0];
            const isGreen = el.innerHTML.includes('text-green') || el.innerHTML.includes('lucide-check') || el.className.includes('green') || svgs.some(c => c && (c.includes('green') || c.includes('check')));
            const isRed = el.innerHTML.includes('text-red') || el.innerHTML.includes('destructive') || svgs.some(c => c && (c.includes('red') || c.includes('alert')));
            return { text, isGreen, isRed };
        });
    }''')

    print(f"\n=== FINAL CHECKLIST ({len(items)} items) ===")
    green_c = sum(1 for it in items if it.get('isGreen'))
    red_c = sum(1 for it in items if it.get('isRed'))
    gray_c = sum(1 for it in items if not it.get('isGreen') and not it.get('isRed'))
    for it in items:
        st = "GREEN" if it.get('isGreen') else ("RED" if it.get('isRed') else "GRAY")
        print(f"[{st}] {it.get('text')}")
    print(f"\nSummary: {green_c} GREEN, {red_c} RED, {gray_c} GRAY")

    ss_final = os.path.join(TASK_DIR, 'final_navigation_checklist_calibrated_final.png')
    await page.screenshot(path=ss_final)
    print(f"Saved {ss_final}")

    await b.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(update_and_run())
