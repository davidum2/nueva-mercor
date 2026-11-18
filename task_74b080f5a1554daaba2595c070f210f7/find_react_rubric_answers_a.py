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

    state = await mercor_page.evaluate("""() => {
        // Search all react fibers for rubricAnswers or answersA or similar
        const root = document.querySelector('#__next') || document.body;
        const key = Object.keys(root).find(k => k.startsWith('__reactFiber$'));
        
        let found = [];
        function walk(fiber, depth=0) {
            if (!fiber || depth > 50) return;
            const props = fiber.memoizedProps;
            if (props) {
                // Check if props has rubricAnswers, rubrics, task, or evaluation
                for (const k of Object.keys(props)) {
                    if (k.toLowerCase().includes('rubric') || k.toLowerCase().includes('answer') || k === 'form' || k === 'values') {
                        try {
                            const valStr = JSON.stringify(props[k]);
                            if (valStr && (valStr.includes('"A"') || valStr.includes('rubric') || valStr.includes('answer'))) {
                                found.push({ key: k, type: fiber.type?.name || typeof fiber.type, preview: valStr.slice(0, 300) });
                            }
                        } catch(e) {}
                    }
                }
            }
            if (fiber.memoizedState) {
                let s = fiber.memoizedState;
                while (s) {
                    try {
                        const valStr = JSON.stringify(s.memoizedState);
                        if (valStr && (valStr.includes('rubricAnswers') || valStr.includes('rubric_answers') || valStr.includes('answer_a') || valStr.includes('A-2') || valStr.includes('A2'))) {
                            found.push({ state: true, preview: valStr.slice(0, 300) });
                        }
                    } catch(e) {}
                    s = s.next;
                }
            }
            walk(fiber.child, depth + 1);
            walk(fiber.sibling, depth);
        }
        walk(root[key]);
        return found.slice(0, 20);
    }""")

    print("Found React state matches:", json.dumps(state, indent=2))

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
