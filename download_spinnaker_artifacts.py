import asyncio
import json
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_08ccf272669347c3af63de71b2ecb5e5'
TASK_DIR = os.path.join(r'c:\desarrollo\nueva-mercor', f'task_task_{TASK_ID}')

async def download_artifacts():
    p = await async_playwright().start()
    b = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [pg for pg in b.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url][0]

    # Fetch file download URLs
    files_to_download = [
        ('agent_a.patch', 'file_0a3f6486937043889a1c451abdecaf13'),
        ('agent_b.patch', 'file_2199e21938354ec9aa8f12fe0b5ce713'),
        ('transcript_A.json', 'file_4f4f78bfde8b41cfb076b879a70ef68c'),
        ('transcript_B.json', 'file_cf51485dedfb41318617f0dd9e058e8e')
    ]

    for fname, fid in files_to_download:
        print(f"Fetching {fname} (fid={fid})...")
        res = await page.evaluate('''async (fid) => {
            const token = await window.Clerk.session.getToken({ skipCache: true });
            const headers = {
                'Authorization': 'Bearer ' + token,
                'Content-Type': 'application/json',
                'x-campaign-id': localStorage.getItem('x-campaign-id') || 'camp_75099d23386f4394ab7596a5ea538da8',
                'x-company-id': localStorage.getItem('x-company-id') || 'comp_2fa4115109d741cd94a3c409ed89e61f',
                'x-account-id': localStorage.getItem('x-account-id') || 'acct_85b680d4c5ba49a29f19c173672aebea'
            };

            // Try GET /files/{id} or /files/{id}/download
            try {
                const r = await fetch(`https://api.studio.mercor.com/files/${fid}`, { headers });
                const data = await r.json();
                return { ok: true, data };
            } catch (e) {
                return { ok: false, error: e.message };
            }
        }''', fid)
        print(f"Result for {fname}:", res)
        if res.get('ok') and isinstance(res.get('data'), dict):
            url = res['data'].get('file_url') or res['data'].get('url') or res['data'].get('download_url')
            if url:
                print(f"Download URL found: {url[:100]}")
                # Fetch url content
                content_res = await page.evaluate('''async (url) => {
                    const r = await fetch(url);
                    return await r.text();
                }''', url)
                with open(os.path.join(TASK_DIR, fname), 'w', encoding='utf-8') as f:
                    f.write(content_res)
                print(f"Saved {fname} ({len(content_res)} chars)")

    await b.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(download_artifacts())
