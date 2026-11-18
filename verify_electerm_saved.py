import asyncio
import json
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_f5ba2eb1464a4db2831f60a63283341d'

async def verify_saved():
    p = await async_playwright().start()
    b = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in b.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    data = await page.evaluate('''async (taskId) => {
        const token = await window.Clerk.session.getToken({ skipCache: true });
        const headers = {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json',
            'x-campaign-id': localStorage.getItem('x-campaign-id') || 'camp_75099d23386f4394ab7596a5ea538da8',
            'x-company-id': localStorage.getItem('x-company-id') || 'comp_2fa4115109d741cd94a3c409ed89e61f',
            'x-account-id': localStorage.getItem('x-account-id') || 'acct_85b680d4c5ba49a29f19c173672aebea'
        };

        const tRes = await fetch(`https://api.studio.mercor.com/tasks/${taskId}`, { headers });
        const task = await tRes.json();
        const cf = task.custom_fields || {};

        const vRes = await fetch(`https://api.studio.mercor.com/verifiers/task/${taskId}`, { headers });
        const verifiers = await vRes.json();

        return {
            task_type: cf.field_task_type,
            rubric_count: cf.field_rubric_count,
            pref: cf.field_e511999a150a45c2b7145f808103d78c,
            score_a: cf.field_ta_final_quality_score_a,
            score_b: cf.field_ta_final_quality_score_b,
            d6_score_a: cf.field_ta_dim6_score_a,
            d6_reason_a: cf.field_ta_dim6_reason_a,
            r01_a: cf.field_ta_rubric_01_answer_a,
            r01_b: cf.field_ta_rubric_01_answer_b,
            r10_a: cf.field_ta_rubric_10_answer_a,
            r10_b: cf.field_ta_rubric_10_answer_b,
            r11_a: cf.field_ta_rubric_11_answer_a,
            verifiers: (verifiers.verifiers || verifiers).map((v, i) => ({
                idx: i + 1,
                crit: v.verifier_values?.criteria,
                ans_a: v.verifier_custom_field_values?.answer_a,
                ans_b: v.verifier_custom_field_values?.answer_b
            }))
        };
    }''', TASK_ID)

    print("=== LIVE SAVED DATA ===")
    print(json.dumps(data, indent=2))

    await b.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(verify_saved())
