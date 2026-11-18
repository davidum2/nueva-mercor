import asyncio
import json
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def check():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url]
    if not task_pages:
        print("No task page found")
        return
    page = task_pages[0]

    data = await page.evaluate("""async (taskId) => {
        const token = await window.Clerk.session.getToken({ skipCache: true });
        const headers = {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json'
        };
        const r = await fetch(`https://api.studio.mercor.com/tasks/${taskId}`, { headers });
        const t = await r.json();
        return {
            status: t.status,
            custom_fields: t.custom_fields,
            adj_rationale: t.custom_fields?.field_adj_rationale,
            comp_rationale: t.custom_fields?.field_1e32bd048d564685ba8ec51f9af11c70
        };
    }""", TASK_ID)

    print("Task Status:", data.get('status'))
    print("\n--- field_1e32bd048d564685ba8ec51f9af11c70 (Comparative Rationale) ---")
    print(data.get('comp_rationale'))
    print("\n--- field_adj_rationale (Adjudication Rationale) ---")
    print(data.get('adj_rationale'))
    print("\nIdentical?", data.get('comp_rationale') == data.get('adj_rationale'))
    print("Lengths:", len(data.get('comp_rationale') or ''), len(data.get('adj_rationale') or ''))

asyncio.run(check())
