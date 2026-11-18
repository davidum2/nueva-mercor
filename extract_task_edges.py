import asyncio
import json
from playwright.async_api import async_playwright

async def main():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [p for ctx in browser.contexts for p in ctx.pages if 'mercor.com' in p.url][0]

    history_data = await page.evaluate('''() => {
        const elements = Array.from(document.querySelectorAll('*'));
        function findReactProps(el) {
            const key = Object.keys(el).find(k => k.startsWith('__reactProps$') || k.startsWith('__reactFiber$'));
            return key ? el[key] : null;
        }

        for (let el of elements) {
            const fiber = findReactProps(el);
            if (!fiber) continue;
            let curr = fiber;
            let depth = 0;
            while (curr && depth < 25) {
                const props = curr.memoizedProps || curr;
                if (props && props.task) {
                    const task = props.task;
                    return {
                        task_edges: task.task_edges,
                        task_latest_edge: task.task_latest_edge,
                        task_history: task.task_history,
                        custom_fields: task.custom_fields,
                        notes: task.notes
                    };
                }
                curr = curr.return;
                depth++;
            }
        }
        return null;
    }''')

    with open('task_74b080f5a1554daaba2595c070f210f7/task_edges_dump.json', 'w', encoding='utf-8') as f:
        json.dump(history_data, f, indent=2, ensure_ascii=False)

    print("History dump saved.")
    if history_data:
        print("Keys found:", list(history_data.keys()))
        if history_data.get('task_latest_edge'):
            print("task_latest_edge keys:", list(history_data['task_latest_edge'].keys()))

if __name__ == "__main__":
    asyncio.run(main())
