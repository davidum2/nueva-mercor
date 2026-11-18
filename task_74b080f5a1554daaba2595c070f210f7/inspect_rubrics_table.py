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

    if not mercor_page:
        print("No page found")
        await browser.close()
        await p.stop()
        return

    rubrics = await mercor_page.evaluate("""() => {
        // Let's find the task state in window or react fiber
        const root = document.querySelector('#__next') || document.body;
        const key = Object.keys(root).find(k => k.startsWith('__reactFiber$'));
        let fiber = root[key];
        
        // Traverse to find custom_fields or rubrics
        let custom_fields = null;
        let queue = [fiber];
        let seen = new Set();
        while (queue.length > 0 && !custom_fields) {
            let cur = queue.shift();
            if (!cur || seen.has(cur)) continue;
            seen.add(cur);
            
            if (cur.memoizedProps && cur.memoizedProps.task && cur.memoizedProps.task.custom_fields) {
                custom_fields = cur.memoizedProps.task.custom_fields;
                break;
            }
            if (cur.child) queue.push(cur.child);
            if (cur.sibling) queue.push(cur.sibling);
        }
        
        return custom_fields;
    }""")

    if rubrics:
        with open('current_custom_fields.json', 'w', encoding='utf-8') as f:
            json.dump(rubrics, f, indent=2)
        print("Successfully extracted current custom_fields!")
        for i in range(1, 16):
            idx = f"{i:02d}"
            print(f"\n--- RUBRIC {i} ---")
            print(f"Criterion: {rubrics.get(f'field_ta_rubric_{idx}_criterion')}")
            print(f"Dim: {rubrics.get(f'field_ta_rubric_{idx}_dim')}")
            print(f"Source: {rubrics.get(f'field_ta_rubric_{idx}_source')}")
            print(f"Ans A: {rubrics.get(f'field_ta_rubric_{idx}_answer_a')} | Ans B: {rubrics.get(f'field_ta_rubric_{idx}_answer_b')}")
            print(f"Reason A: {rubrics.get(f'field_ta_rubric_{idx}_reason_a')[:80]}...")
            print(f"Reason B: {rubrics.get(f'field_ta_rubric_{idx}_reason_b')[:80]}...")
    else:
        print("Could not find custom_fields via fiber traversal")

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
