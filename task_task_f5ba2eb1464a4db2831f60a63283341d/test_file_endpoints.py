import asyncio
import json
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_f5ba2eb1464a4db2831f60a63283341d'

async def test_file_api():
    p = await async_playwright().start()
    b = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [pg for pg in b.contexts[0].pages if TASK_ID in pg.url and 'rubric' not in pg.url][0]
    
    file_id = 'file_d9b7918df11a45beaab142029893bd23'
    s3_url = 's3://rl-studio-snapshots-prod/files/camp_75099d23386f4394ab7596a5ea538da8/file_d9b7918df11a45beaab142029893bd23_transcript_A.json'

    res = await page.evaluate('''async ({ fId, s3 }) => {
        const token = await window.Clerk.session.getToken();
        const headers = { 
            'Authorization': 'Bearer ' + token,
            'x-campaign-id': localStorage.getItem('x-campaign-id') || 'camp_75099d23386f4394ab7596a5ea538da8',
            'x-company-id': localStorage.getItem('x-company-id') || 'comp_2fa4115109d741cd94a3c409ed89e61f',
            'x-account-id': localStorage.getItem('x-account-id') || 'acct_85b680d4c5ba49a29f19c173672aebea'
        };

        const tests = [
            `https://api.studio.mercor.com/files/${fId}`,
            `https://api.studio.mercor.com/files/${fId}/download`,
            `https://api.studio.mercor.com/files/download?file_id=${fId}`,
            `https://api.studio.mercor.com/files/download?s3_url=${encodeURIComponent(s3)}`,
            `https://api.studio.mercor.com/files/url?s3_url=${encodeURIComponent(s3)}`
        ];

        const out = {};
        for (const u of tests) {
            try {
                const r = await fetch(u, { headers });
                out[u] = { status: r.status };
                if (r.ok) {
                    const ct = r.headers.get('content-type') || '';
                    if (ct.includes('json')) {
                        out[u].json = await r.json();
                    } else {
                        const txt = await r.text();
                        out[u].len = txt.length;
                        out[u].sample = txt.substring(0, 100);
                    }
                }
            } catch(e) {
                out[u] = { error: e.message };
            }
        }
        return out;
    }''', {'fId': file_id, 's3': s3_url})

    print(json.dumps(res, indent=2))
    await b.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(test_file_api())
