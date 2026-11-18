import asyncio
import json
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_f5ba2eb1464a4db2831f60a63283341d'
TASK_DIR = os.path.join(r'c:\desarrollo\nueva-mercor', f'task_{TASK_ID}')
os.makedirs(TASK_DIR, exist_ok=True)
os.makedirs(os.path.join(TASK_DIR, 'bundle'), exist_ok=True)
os.makedirs(os.path.join(TASK_DIR, 'model_a'), exist_ok=True)
os.makedirs(os.path.join(TASK_DIR, 'model_b'), exist_ok=True)

async def dump_task_page_details():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    if not task_pages:
        print("Task page not found among open tabs!")
        await p.stop()
        return
    page = task_pages[0]

    # 1. Inspect sidebar navigation items
    tabs_info = await page.evaluate('''() => {
        const buttons = Array.from(document.querySelectorAll('button, div[role="tab"]')).map(b => ({
            text: b.innerText ? b.innerText.trim() : '',
            classes: b.className
        }));
        return buttons.filter(b => b.text.length > 0 && b.text.length < 80);
    }''')
    print("=== SIDEBAR / PAGE TABS ===")
    seen = set()
    for t in tabs_info:
        txt = t['text']
        if txt not in seen:
            seen.add(txt)
            if any(k in txt.lower() for k in ['bundle', 'model', 'side', 'transcript', 'rubric', 'dimension', 'submit', 'qc', 'feedback', 'autoqc', 'evaluation']):
                print(" ->", repr(txt))

    # 2. Get signed URLs for transcripts or artifacts from Mercor API
    files_res = await page.evaluate('''async (taskId) => {
        const token = await window.Clerk.session.getToken({ skipCache: true });
        const headers = {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json',
            'x-campaign-id': localStorage.getItem('x-campaign-id') || 'camp_75099d23386f4394ab7596a5ea538da8',
            'x-company-id': localStorage.getItem('x-company-id') || 'comp_2fa4115109d741cd94a3c409ed89e61f',
            'x-account-id': localStorage.getItem('x-account-id') || 'acct_85b680d4c5ba49a29f19c173672aebea'
        };

        const res = await fetch(`https://api.studio.mercor.com/tasks/${taskId}`, { headers });
        const data = await res.json();
        const cf = data.custom_fields || {};

        return {
            cf: cf,
            transcript_a: cf.transcript_file_a,
            transcript_b: cf.transcript_file_b,
            artifact_a: cf.artifact_files_a,
            artifact_b: cf.artifact_files_b
        };
    }''', TASK_ID)

    with open(os.path.join(TASK_DIR, 'custom_fields.json'), 'w', encoding='utf-8') as f:
        json.dump(files_res['cf'], f, indent=2)

    # Let's download transcript files
    for side, t_val in [('A', files_res['transcript_a']), ('B', files_res['transcript_b'])]:
        print(f"\n--- Checking Transcript {side} ---")
        print("Raw value:", repr(t_val))
        if isinstance(t_val, str):
            try:
                t_val = json.loads(t_val)
            except:
                pass
        if isinstance(t_val, list) and len(t_val) > 0:
            first_item = t_val[0]
            url = first_item.get('file_s3_url') or first_item.get('url')
            print(f"Transcript {side} URL: {url}")
            # If it's an S3 URL or Mercor signed URL, let's see if page can fetch a signed download URL
            dl_res = await page.evaluate('''async (s3Url) => {
                const token = await window.Clerk.session.getToken({ skipCache: true });
                const headers = { 'Authorization': 'Bearer ' + token };
                // Try fetching signed url
                const res = await fetch(`https://api.studio.mercor.com/files/signed-url?s3_url=${encodeURIComponent(s3Url)}`, { headers });
                if (res.ok) {
                    const data = await res.json();
                    return data.signed_url || data.url;
                }
                return null;
            }''', url)
            print(f"Signed download URL for {side}: {dl_res}")
            if dl_res:
                content = await page.evaluate('''async (url) => {
                    const r = await fetch(url);
                    return await r.text();
                }''', dl_res)
                out_path = os.path.join(TASK_DIR, f'model_{side.lower()}', f'transcript_{side}.json')
                with open(out_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Downloaded transcript {side} ({len(content)} bytes) to {out_path}")

    await p.stop()

if __name__ == '__main__':
    asyncio.run(dump_task_page_details())
