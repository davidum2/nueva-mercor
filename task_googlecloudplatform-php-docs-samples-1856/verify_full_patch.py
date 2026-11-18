import asyncio
import json
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def verify_patch():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
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

        const taskRes = await fetch(`https://api.studio.mercor.com/tasks/${taskId}`, { headers });
        const task = await taskRes.json();
        const vRes = await fetch(`https://api.studio.mercor.com/verifiers/task/${taskId}`, { headers });
        const verifiers = await vRes.json();

        return {
            cf: task.custom_fields,
            verifiers: verifiers.verifiers || verifiers
        };
    }''', TASK_ID)

    cf = data['cf']
    print("=== CUSTOM FIELDS VERIFICATION ===")
    print("field_rubric_count:", repr(cf.get('field_rubric_count')))
    print("field_ta_dim2_score_a:", cf.get('field_ta_dim2_score_a'))
    print("field_ta_dim8_reason_b (first 100):", repr((cf.get('field_ta_dim8_reason_b') or '')[:100]))
    print("field_1e32bd048d564685ba8ec51f9af11c70 (first 100):", repr((cf.get('field_1e32bd048d564685ba8ec51f9af11c70') or '')[:100]))
    print("field_adj_rationale (first 100):", repr((cf.get('field_adj_rationale') or '')[:100]))
    print("Rationales identical?", cf.get('field_1e32bd048d564685ba8ec51f9af11c70') == cf.get('field_adj_rationale'))

    print("\n--- Rubrics 1 to 9 ---")
    yes_a = 0
    yes_b = 0
    for i in range(1, 10):
        si = f'{i:02d}'
        a = cf.get(f'field_ta_rubric_{si}_answer_a')
        b = cf.get(f'field_ta_rubric_{si}_answer_b')
        ra = cf.get(f'field_ta_rubric_{si}_reason_a') or ''
        rb = cf.get(f'field_ta_rubric_{si}_reason_b') or ''
        if a == 'YES': yes_a += 1
        if b == 'YES': yes_b += 1
        print(f"R{si}: A={a} ({len(ra)} chars) | B={b} ({len(rb)} chars)")

    print(f"\nModel A YES rate: {yes_a}/9 = {yes_a/9*100:.2f}% (Strictly < 75%: {yes_a/9 < 0.75})")
    print(f"Model B YES rate: {yes_b}/9 = {yes_b/9*100:.2f}% (Strictly < 75%: {yes_b/9 < 0.75})")

    print("\n--- Residual Rubrics 10 to 15 in CF ---")
    residual_populated = []
    for i in range(10, 16):
        si = f'{i:02d}'
        for suffix in ['answer_a', 'answer_b', 'reason_a', 'reason_b', 'mapped_dimension_a', 'mapped_dimension_b']:
            k = f'field_ta_rubric_{si}_{suffix}'
            val = cf.get(k)
            if val is not None and val != "":
                residual_populated.append(f"{k} = {repr(val)}")
    
    if residual_populated:
        print("WARNING: Some residual fields still populated:")
        for r in residual_populated:
            print(" ", r)
    else:
        print("PERFECT: ZERO residual fields populated for 10-15!")

    await p.stop()

if __name__ == '__main__':
    asyncio.run(verify_patch())
