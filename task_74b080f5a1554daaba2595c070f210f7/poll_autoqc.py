import asyncio
import sys
from playwright.async_api import async_playwright

async def run():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    mercor_page = None
    for ctx in browser.contexts:
        for page in ctx.pages:
            if 'mercor.com' in page.url:
                mercor_page = page
                break
        if mercor_page:
            break

    for attempt in range(12): # poll for up to 2 minutes
        status = await mercor_page.evaluate("""() => {
            const text = document.body.innerText;
            const isRunning = text.includes('AutoQC is running');
            const lines = text.split('\\n').map(l => l.trim()).filter(Boolean);
            const autoqcIdx = lines.findIndex(l => l === 'DELIVERABLE AUTOQC');
            const snippet = autoqcIdx !== -1 ? lines.slice(autoqcIdx, autoqcIdx + 25) : [];
            
            // Check issues count
            const issues = {
                all: lines.find(l => l.startsWith('All (')) || 'All',
                major: lines.find(l => l.startsWith('Major issues (')) || lines.find(l => l === 'Major issues'),
                minor: lines.find(l => l.startsWith('Minor issues (')) || lines.find(l => l === 'Minor issues'),
                passed: lines.find(l => l.startsWith('Passed (')) || lines.find(l => l === 'Passed')
            };
            
            return { isRunning, snippet, issues };
        }""")
        
        print(f"[{attempt*10}s] Running: {status['isRunning']} | Issues: {status['issues']}")
        if not status['isRunning'] and attempt > 0:
            print("AutoQC finished running! Snippet:")
            for s in status['snippet']:
                # print ascii safe
                print(" ", s.encode('ascii', errors='replace').decode('ascii'))
            break
            
        await asyncio.sleep(10.0)

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
