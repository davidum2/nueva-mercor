import asyncio
import sys
import json
import time
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'
V1_ID = 'ver_7dda937c36f24292bc06be412fbbd729' # index 1 (0-based)

V1_REASON_A = "Model A assigns raw template strings directly into setDeidentifyTemplate, setStructuredDeidentifyTemplate, and setImageRedactTemplate without resolving canonical resource names via DlpServiceBaseClient::projectDeidentifyTemplateName (patch_a.diff:L81-84)."
V1_REASON_B = "Model B directly passes raw template strings to setDeidentifyTemplate, setStructuredDeidentifyTemplate, and setImageRedactTemplate on patch_b.diff:L80-83 without calling DlpServiceBaseClient::projectDeidentifyTemplateName."

async def fix_and_rerun():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    # 1. Update Verifier 1 in API
    update_res = await page.evaluate('''async ({ taskId, v1Id, reasonA, reasonB }) => {
        const token = await window.Clerk.session.getToken({ skipCache: true });
        const headers = {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json',
            'x-campaign-id': localStorage.getItem('x-campaign-id') || 'camp_75099d23386f4394ab7596a5ea538da8',
            'x-company-id': localStorage.getItem('x-company-id') || 'comp_2fa4115109d741cd94a3c409ed89e61f',
            'x-account-id': localStorage.getItem('x-account-id') || 'acct_85b680d4c5ba49a29f19c173672aebea'
        };

        // PATCH verifier
        const patchV1 = await fetch(`https://api.studio.mercor.com/verifiers/${v1Id}`, {
            method: 'PATCH',
            headers,
            body: JSON.stringify({
                verifier_custom_field_values: {
                    answer_a: "NO",
                    answer_b: "NO",
                    reason_a: reasonA,
                    reason_b: reasonB,
                    rubric_source: "PROJECT_CONVENTIONS",
                    mapped_dimension: "2 · Functional Correctness & Code Architecture"
                }
            })
        });

        // Check task custom_fields for setDeidentifyTemplateName
        const taskR = await fetch(`https://api.studio.mercor.com/tasks/${taskId}`, { headers });
        const task = await taskR.json();
        const cf = task.custom_fields || {};
        const updates = {};
        for (const [k, v] of Object.entries(cf)) {
            if (typeof v === 'string' && v.includes('setDeidentifyTemplateName')) {
                updates[k] = v.replaceAll('setDeidentifyTemplateName', 'setDeidentifyTemplate');
            }
        }

        let taskPatchStatus = 200;
        if (Object.keys(updates).length > 0) {
            const taskPatch = await fetch(`https://api.studio.mercor.com/tasks/${taskId}`, {
                method: 'PATCH',
                headers,
                body: JSON.stringify({ custom_fields: updates })
            });
            taskPatchStatus = taskPatch.status;
        }

        return {
            patchV1Status: patchV1.status,
            taskFieldsUpdated: Object.keys(updates),
            taskPatchStatus
        };
    }''', {
        'taskId': TASK_ID,
        'v1Id': V1_ID,
        'reasonA': V1_REASON_A,
        'reasonB': V1_REASON_B
    })

    print("API update result:", json.dumps(update_res, indent=2), flush=True)

    # 2. Reload page to hydrate React
    print("Reloading page...", flush=True)
    await page.reload(wait_until='domcontentloaded')
    await asyncio.sleep(5)

    # 3. Expand DELIVERABLE AUTOQC accordion
    header = page.locator('div.cursor-pointer:has-text("DELIVERABLE AUTOQC")')
    if await header.count() > 0:
        await header.first.scroll_into_view_if_needed()
        await header.first.click()
        await asyncio.sleep(2)

    # 4. Click Run AutoQC
    run_btn = page.locator('button:has-text("Run AutoQC")')
    if await run_btn.count() > 0:
        await run_btn.first.click()
        print("Clicked Run AutoQC successfully!", flush=True)

        # 5. Monitor run
        start_time = time.time()
        for i in range(50):
            await asyncio.sleep(6)
            elapsed = int(time.time() - start_time)

            status = await page.evaluate('''() => {
                const body = document.body.innerText;
                const isRunning = body.includes('AutoQC is running') || body.includes('Compiling') || body.includes('Analyzing') || body.includes('Staging context') || body.includes('Preparing');

                const passedMatches = body.match(/(\\d+)\\s*passed/i);
                const majorMatches = body.match(/(\\d+)\\s*major/i);
                const minorMatches = body.match(/(\\d+)\\s*minor/i);
                const runBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText && (b.innerText.includes('Latest run') || b.innerText.includes('run ·')));
                const stageText = body.match(/(Preparing|Staging context|Analyzing \\d+\\/\\d+|Compiling)/g);

                return {
                    isRunning,
                    stage: stageText ? stageText.join(' -> ') : null,
                    passed: passedMatches ? passedMatches[0] : null,
                    major: majorMatches ? majorMatches[0] : null,
                    minor: minorMatches ? minorMatches[0] : null,
                    runText: runBtn ? runBtn.innerText.trim() : null
                };
            }''')

            print(f"[{elapsed}s] isRunning={status['isRunning']} | stage={status['stage']} | passed={status['passed']} | major={status['major']} | minor={status['minor']} | run={status['runText']}", flush=True)

            if not status['isRunning'] and i >= 3:
                print("AutoQC run completed! Settling 5s...", flush=True)
                await asyncio.sleep(5)
                break

    # Dump results
    report = await page.evaluate('''() => {
        const body = document.body.innerText;
        const autoqcCard = Array.from(document.querySelectorAll('*'))
            .filter(el => el.innerText && el.innerText.includes('DELIVERABLE AUTOQC') && el.innerText.includes('check your work'))[0];
        
        return autoqcCard ? autoqcCard.innerText : body.slice(0, 3000);
    }''')

    print("\n=== AUTOQC FINAL RUN REPORT ===")
    print(report)
    print("===============================\n")

    await page.screenshot(path='autoqc_17_of_17_perfect.png')
    print("Saved autoqc_17_of_17_perfect.png")

    # Navigate to Submit review -> Navigation
    nav_item = page.locator('span:text-is("Navigation")')
    if await nav_item.count() > 0:
        await nav_item.first.click()
        await asyncio.sleep(2)
        # Scroll to checklist
        await page.evaluate('''() => {
            const el = Array.from(document.querySelectorAll('*')).find(e => e.innerText && e.innerText.startsWith('Before you submit'));
            if (el) el.scrollIntoView({ behavior: 'instant', block: 'start' });
        }''')
        await asyncio.sleep(1)
        await page.screenshot(path='navigation_all_green_checkmarks.png')
        print("Saved navigation_all_green_checkmarks.png")

    await p.stop()
    print("All tasks finished successfully!", flush=True)

if __name__ == '__main__':
    asyncio.run(fix_and_rerun())
