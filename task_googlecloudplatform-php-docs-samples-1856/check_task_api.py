import asyncio
import json
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True)

TASK_ID = "task_a6c044440a2b440a9d578ad5c375ad94"

async def check_task_api():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url]
    page = task_pages[0]
    
    result = await page.evaluate("""async ({ taskId }) => {
        const token = await window.Clerk.session.getToken({ skipCache: true });
        const headers = {
            'Authorization': 'Bearer ' + token,
            'x-campaign-id': localStorage.getItem('x-campaign-id') || 'camp_75099d23386f4394ab7596a5ea538da8',
            'x-company-id': localStorage.getItem('x-company-id') || 'comp_2fa4115109d741cd94a3c409ed89e61f',
            'x-account-id': localStorage.getItem('x-account-id') || 'acct_85b680d4c5ba49a29f19c173672aebea'
        };
        const r = await fetch(`https://api.studio.mercor.com/tasks/${taskId}`, { headers });
        const d = await r.json();
        return {
            status: r.status,
            task_id: d.task_id,
            updated_at: d.updated_at,
            custom_fields: d.custom_fields
        };
    }""", { "taskId": TASK_ID })

    print("Task Status:", result['status'])
    print("Updated at:", result['updated_at'])
    cf = result.get('custom_fields', {})
    print("field_rubric_count:", cf.get('field_rubric_count'))
    print("field_ta_final_quality_score_a:", cf.get('field_ta_final_quality_score_a'))
    print("field_ta_final_quality_score_b:", cf.get('field_ta_final_quality_score_b'))
    print("field_e511999a150a45c2b7145f808103d78c:", cf.get('field_e511999a150a45c2b7145f808103d78c'))
    print("Rationale (first 100 chars):", cf.get('field_adj_rationale', '')[:100])
    
    print("\nRubrics in task custom_fields:")
    for i in range(1, 14):
        num = f"{i:02d}"
        ans_a = cf.get(f'field_ta_rubric_{num}_answer_a')
        ans_b = cf.get(f'field_ta_rubric_{num}_answer_b')
        dim_a = cf.get(f'field_ta_rubric_{num}_mapped_dimension_a')
        print(f"  Rubric {num}: A={ans_a} | B={ans_b} | Dim={dim_a}")

    print("\nDimensions 2-9 Scores:")
    for d in range(2, 10):
        sa = cf.get(f'field_ta_dim{d}_score_a')
        sb = cf.get(f'field_ta_dim{d}_score_b')
        print(f"  Dim {d}: A={sa} | B={sb}")

    with open('verified_task_custom_fields.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)

    await p.stop()

if __name__ == '__main__':
    asyncio.run(check_task_api())
