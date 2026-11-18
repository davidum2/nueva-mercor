import asyncio
import json
import sys
import time
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_a6c044440a2b440a9d578ad5c375ad94'

async def poll_autoqc():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    if not task_pages:
        print("No task page found!")
        await p.stop()
        return
    page = task_pages[0]

    print("Polling AutoQC status...", flush=True)

    for i in range(25): # poll up to ~100 seconds
        status = await page.evaluate("""() => {
            const bodyText = document.body.innerText;
            const isRunning = bodyText.includes('AutoQC is running') || bodyText.includes('Running AutoQC...');
            
            // Check AutoQC tab or issues
            const majorIssues = Array.from(document.querySelectorAll('*')).filter(el => el.innerText && el.innerText.includes('major issue'));
            const passedTests = Array.from(document.querySelectorAll('*')).filter(el => el.innerText && el.innerText.includes('passed'));
            
            // Runs selector text
            const runButtons = Array.from(document.querySelectorAll('button')).map(b => b.innerText ? b.innerText.trim() : '');
            
            return {
                isRunning,
                runButtons: runButtons.filter(t => t.includes('Run') || t.includes('AutoQC')),
                hasMajorIssueText: bodyText.includes('major issue'),
                hasPassedText: bodyText.includes('passed')
            };
        }""")
        print(f"[{i+1}/25] isRunning={status['isRunning']}, runButtons={status['runButtons']}", flush=True)

        if not status['isRunning'] and i > 2:
            print("AutoQC completed or not running! Waiting 3 seconds for UI settling...", flush=True)
            await asyncio.sleep(3)
            break
        await asyncio.sleep(4)

    # Make sure we are on Deliverable AutoQC tab or take detailed screenshots
    autoqc_tab = page.locator('button:has-text("Deliverable AutoQC")')
    if await autoqc_tab.count() > 0:
        await autoqc_tab.first.click()
        await asyncio.sleep(2)

    # Extract all test item results from Deliverable AutoQC
    results = await page.evaluate("""() => {
        // Collect text from test items
        const items = [];
        const nodes = document.querySelectorAll('[role="tabpanel"], div[class*="autoqc"], div[class*="AutoQC"]');
        
        // Find all elements containing 'Test' or checkmarks or issues
        const cards = Array.from(document.querySelectorAll('div')).filter(d => {
            const t = d.innerText || '';
            return (t.includes('Passed') || t.includes('Failed') || t.includes('Issue')) && d.children.length > 0 && d.children.length < 10;
        });

        return {
            bodySnippet: document.body.innerText.substring(0, 3000),
            cardsCount: cards.length
        };
    }""")

    screenshot_path = 'autoqc_latest_results.png'
    await page.screenshot(path=screenshot_path, full_page=False)
    print(f"Saved screenshot to {screenshot_path}", flush=True)

    # Also click on Submit Review tab to see checklist
    submit_tab = page.locator('button:has-text("Submit review")')
    if await submit_tab.count() > 0:
        await submit_tab.first.click()
        await asyncio.sleep(2)
        submit_screen = 'submit_review_tab.png'
        await page.screenshot(path=submit_screen, full_page=False)
        print(f"Saved submit review checklist screenshot to {submit_screen}", flush=True)

    await p.stop()
    print("Done polling!", flush=True)

if __name__ == '__main__':
    asyncio.run(poll_autoqc())
