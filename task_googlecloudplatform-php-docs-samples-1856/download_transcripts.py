import os
import json
import asyncio
from playwright.async_api import async_playwright

DEST_DIR = r"c:\desarrollo\nueva-mercor\task_a6c044440a2b440a9d578ad5c375ad94"

async def extract_bundle_and_transcripts():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = browser.contexts[0].pages[0]

    with open(os.path.join(DEST_DIR, "task_api_dump.json"), "r", encoding="utf-8") as f:
        api_data = json.load(f)

    cf = api_data.get('task', {}).get('custom_fields', {})
    
    # Transcript URLs
    trans_a = cf.get('transcript_file_a')
    trans_b = cf.get('transcript_file_b')
    artifacts_a = cf.get('artifact_files_a')
    artifacts_b = cf.get('artifact_files_b')

    print("Transcript A URL:", trans_a)
    print("Transcript B URL:", trans_b)

    download_script = """async (files) => {
        const token = await window.Clerk.session.getToken();
        const headers = { 'Authorization': 'Bearer ' + token };
        const results = {};
        for (const [k, urlList] of Object.entries(files)) {
            if (!urlList || !urlList.length) continue;
            const url = typeof urlList === 'string' ? urlList : (urlList[0]?.url || urlList[0]);
            try {
                const r = await fetch(url);
                if (r.ok) {
                    results[k] = await r.text();
                } else {
                    results[k] = `error: status ${r.status}`;
                }
            } catch(e) {
                results[k] = `error: ${e.message}`;
            }
        }
        return results;
    }"""

    files_to_fetch = {
        'transcript_a': trans_a,
        'transcript_b': trans_b,
        'artifact_a': artifacts_a,
        'artifact_b': artifacts_b
    }

    res = await page.evaluate(download_script, files_to_fetch)

    # Save transcripts
    if 'transcript_a' in res and not res['transcript_a'].startswith('error'):
        with open(os.path.join(DEST_DIR, "model_a", "transcript_a.json"), "w", encoding="utf-8") as f:
            f.write(res['transcript_a'])
        print(f"Saved transcript A ({len(res['transcript_a'])} bytes)")
    else:
        print("Transcript A error:", res.get('transcript_a'))

    if 'transcript_b' in res and not res['transcript_b'].startswith('error'):
        with open(os.path.join(DEST_DIR, "model_b", "transcript_b.json"), "w", encoding="utf-8") as f:
            f.write(res['transcript_b'])
        print(f"Saved transcript B ({len(res['transcript_b'])} bytes)")
    else:
        print("Transcript B error:", res.get('transcript_b'))

    # Save artifacts
    if 'artifact_a' in res and not res['artifact_a'].startswith('error'):
        with open(os.path.join(DEST_DIR, "model_a", "artifact_a.patch"), "w", encoding="utf-8") as f:
            f.write(res['artifact_a'])
        print(f"Saved artifact A ({len(res['artifact_a'])} bytes)")

    if 'artifact_b' in res and not res['artifact_b'].startswith('error'):
        with open(os.path.join(DEST_DIR, "model_b", "artifact_b.patch"), "w", encoding="utf-8") as f:
            f.write(res['artifact_b'])
        print(f"Saved artifact B ({len(res['artifact_b'])} bytes)")

    # Fetch bundle files from page DOM or bundle explorer if present
    bundle_files = await page.evaluate("""() => {
        // Find file tree in bundle explorer
        const els = Array.from(document.querySelectorAll('*')).filter(el => {
            return (el.innerText || '').trim() === 'EXPLORER' && el.children.length === 0;
        });
        if (els.length > 0) {
            const exp = els[0].parentElement;
            return exp ? exp.innerText : 'no parent';
        }
        return 'no explorer';
    }""")
    print("Bundle Explorer text:\n", bundle_files)

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(extract_bundle_and_transcripts())
