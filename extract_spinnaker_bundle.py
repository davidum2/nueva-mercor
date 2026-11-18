import asyncio
import json
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_08ccf272669347c3af63de71b2ecb5e5'
TASK_DIR = os.path.join(r'c:\desarrollo\nueva-mercor', f'task_{TASK_ID}')

async def inspect_bundle():
    p = await async_playwright().start()
    b = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [pg for pg in b.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url][0]

    # Click Task bundle tab in sidebar
    print("Clicking Task bundle in sidebar...")
    await page.evaluate('''() => {
        const btns = Array.from(document.querySelectorAll('button, div, span'));
        const tab = btns.find(b => b.innerText && b.innerText.trim() === 'Task bundle');
        if (tab) tab.click();
    }''')
    await asyncio.sleep(2)

    # Extract all files listed in bundle
    bundle_files = await page.evaluate('''() => {
        const fileBtns = Array.from(document.querySelectorAll('button')).filter(b => {
            const t = (b.innerText || '').trim();
            return t.includes('.patch') || t.includes('.sh') || t.includes('.py') || t.includes('.md') || t.includes('Dockerfile') || t.includes('.json') || t.includes('.ts');
        }).map(b => b.innerText.trim());
        return fileBtns;
    }''')
    print("Bundle files listed in UI:", bundle_files)

    # Let's inspect history entries
    history_info = await page.evaluate('''async (taskId) => {
        const token = await window.Clerk.session.getToken({ skipCache: true });
        const headers = {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json',
            'x-campaign-id': localStorage.getItem('x-campaign-id') || 'camp_75099d23386f4394ab7596a5ea538da8',
            'x-company-id': localStorage.getItem('x-company-id') || 'comp_2fa4115109d741cd94a3c409ed89e61f',
            'x-account-id': localStorage.getItem('x-account-id') || 'acct_85b680d4c5ba49a29f19c173672aebea'
        };

        const hRes = await fetch(`https://api.studio.mercor.com/tasks/${taskId}/history`, { headers });
        const hData = await hRes.json();
        return hData;
    }''', TASK_ID)

    with open(os.path.join(TASK_DIR, 'history_api.json'), 'w', encoding='utf-8') as f:
        json.dump(history_info, f, indent=2, ensure_ascii=False)
    print(f"Saved history_api.json")

    # Let's also inspect AutoQC audits
    qc_info = await page.evaluate('''async (taskId) => {
        const token = await window.Clerk.session.getToken({ skipCache: true });
        const headers = {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json',
            'x-campaign-id': localStorage.getItem('x-campaign-id') || 'camp_75099d23386f4394ab7596a5ea538da8',
            'x-company-id': localStorage.getItem('x-company-id') || 'comp_2fa4115109d741cd94a3c409ed89e61f',
            'x-account-id': localStorage.getItem('x-account-id') || 'acct_85b680d4c5ba49a29f19c173672aebea'
        };

        const qcRes = await fetch(`https://api.studio.mercor.com/qc_audits/task/${taskId}`, { headers });
        const qcData = await qcRes.json();
        return qcData;
    }''', TASK_ID)

    with open(os.path.join(TASK_DIR, 'qc_audits_api.json'), 'w', encoding='utf-8') as f:
        json.dump(qc_info, f, indent=2, ensure_ascii=False)
    print(f"Saved qc_audits_api.json")

    await b.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(inspect_bundle())
