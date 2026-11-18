import asyncio
import json
from playwright.async_api import async_playwright

async def main():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [p for ctx in browser.contexts for p in ctx.pages if 'mercor.com' in p.url][0]

    data = await page.evaluate('''() => {
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
                    return {
                        taskCustomFields: props.task.custom_fields,
                        taskNotes: props.task.notes,
                        allTaskKeys: Object.keys(props.task)
                    };
                }
                curr = curr.return;
                depth++;
            }
        }
        return null;
    }''')

    with open('task_74b080f5a1554daaba2595c070f210f7/task_fiber_dump.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("Task custom_fields keys:", list(data['taskCustomFields'].keys()) if data and data.get('taskCustomFields') else "None")

if __name__ == "__main__":
    asyncio.run(main())
