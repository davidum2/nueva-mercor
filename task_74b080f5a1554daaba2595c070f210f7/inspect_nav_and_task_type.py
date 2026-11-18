import asyncio
import json
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

    # Look at all top-level tabs or navigation buttons
    nav_info = await mercor_page.evaluate("""() => {
        const tabs = Array.from(document.querySelectorAll('[role="tab"], button[data-state], nav a, nav button'));
        return tabs.map(t => ({
            tag: t.tagName,
            role: t.getAttribute('role'),
            text: (t.innerText || '').trim(),
            state: t.getAttribute('data-state'),
            ariaSelected: t.getAttribute('aria-selected')
        }));
    }""")
    print("Tabs / Nav:", json.dumps(nav_info, indent=2))

    # Look at where Task type dropdown is located
    task_type_info = await mercor_page.evaluate("""() => {
        // Search text for 'Task type'
        const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
        const results = [];
        let node;
        while (node = walker.nextNode()) {
            if (node.nodeValue && node.nodeValue.includes('Task type')) {
                const parent = node.parentElement;
                results.push({
                    text: node.nodeValue.trim(),
                    parentTag: parent.tagName,
                    parentText: (parent.innerText || '').slice(0, 100).replace(/\\n/g, ' '),
                    grandParentText: (parent.parentElement?.innerText || '').slice(0, 200).replace(/\\n/g, ' ')
                });
            }
        }
        return results;
    }""")
    print("Task type text locations:", json.dumps(task_type_info, indent=2))

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
