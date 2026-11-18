import asyncio
import os
import json
from playwright.async_api import async_playwright

TASK_ID = "task_a6c044440a2b440a9d578ad5c375ad94"
CAMPAIGN_ID = "camp_75099d23386f4394ab7596a5ea538da8"
TASK_URL = f"https://studio.mercor.com/annotator/tasks/{TASK_ID}/?campaignId={CAMPAIGN_ID}"
DEST_DIR = os.path.join(r"c:\desarrollo\nueva-mercor", TASK_ID)

os.makedirs(DEST_DIR, exist_ok=True)
os.makedirs(os.path.join(DEST_DIR, "bundle"), exist_ok=True)
os.makedirs(os.path.join(DEST_DIR, "model_a"), exist_ok=True)
os.makedirs(os.path.join(DEST_DIR, "model_b"), exist_ok=True)
os.makedirs(os.path.join(DEST_DIR, "tabs"), exist_ok=True)

print(f"Created directories for {TASK_ID} at {DEST_DIR}")

async def run():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    ctx = browser.contexts[0]

    # Find an existing mercor task page to navigate, or create one
    mercor_page = None
    for pg in ctx.pages:
        if 'studio.mercor.com/annotator/tasks/' in pg.url:
            mercor_page = pg
            break

    if not mercor_page:
        print("No existing task page, creating new page in context...")
        mercor_page = await ctx.new_page()

    print(f"Navigating to {TASK_URL}...")
    await mercor_page.goto(TASK_URL)
    await asyncio.sleep(5.0)

    # Fetch task data from API
    api_data = await mercor_page.evaluate("""async (taskId) => {
        const token = await window.Clerk.session.getToken();
        const campaignId = localStorage.getItem('x-campaign-id') || 'camp_75099d23386f4394ab7596a5ea538da8';
        const companyId = localStorage.getItem('x-company-id') || '';
        const accountId = localStorage.getItem('x-account-id') || '';
        const headers = {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json',
            'x-campaign-id': campaignId,
            'x-company-id': companyId,
            'x-account-id': accountId
        };
        
        const urls = {
            task: `https://api.studio.mercor.com/tasks/${taskId}`,
            history: `https://api.studio.mercor.com/tasks/${taskId}/history`,
            related: `https://api.studio.mercor.com/tasks/${taskId}/related`
        };

        const res = {};
        for (const [k, url] of Object.entries(urls)) {
            try {
                const r = await fetch(url, { headers });
                if (r.ok) {
                    res[k] = await r.json();
                } else {
                    res[k] = { status: r.status, statusText: r.statusText, text: await r.text() };
                }
            } catch(e) {
                res[k] = { error: e.message };
            }
        }
        return res;
    }""", TASK_ID)

    task_json_path = os.path.join(DEST_DIR, "task_api_dump.json")
    with open(task_json_path, 'w', encoding='utf-8') as f:
        json.dump(api_data, f, indent=2, ensure_ascii=False)
    print(f"Dumped API data to {task_json_path}")

    # Extract high level info
    t = api_data.get('task', {})
    print("\n--- Task Info ---")
    print(f"Task Name: {t.get('task_name')}")
    print(f"Status: {t.get('task_status_defn', {}).get('name') if t.get('task_status_defn') else t.get('task_status_id')}")
    print(f"Review Feedback: {t.get('review_feedback')}")

    cf = t.get('custom_fields', {})
    cf_path = os.path.join(DEST_DIR, "custom_fields.json")
    with open(cf_path, 'w', encoding='utf-8') as f:
        json.dump(cf, f, indent=2, ensure_ascii=False)
    print(f"Dumped custom fields ({len(cf)} keys) to {cf_path}")

    # Check model names and language
    print(f"Language: {cf.get('field_language')}")
    print(f"Repo: {cf.get('field_repo_url')}")
    print(f"Problem: {cf.get('field_problem_title')}")
    print(f"Difficulty: {cf.get('field_difficulty')}")
    print(f"Model A: {cf.get('field_model_a')}")
    print(f"Model B: {cf.get('field_model_b')}")
    print(f"Gemini Side: {cf.get('field_gemini_side')}")

    # Take screenshot of new task page
    screenshot_path = os.path.join(DEST_DIR, "task_initial_screenshot.png")
    await mercor_page.screenshot(path=screenshot_path)
    print(f"Initial screenshot saved to {screenshot_path}")

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
