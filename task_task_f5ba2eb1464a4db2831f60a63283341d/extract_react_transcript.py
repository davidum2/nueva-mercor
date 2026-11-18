import asyncio
import json
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_f5ba2eb1464a4db2831f60a63283341d'

async def extract_transcript_from_react():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    task_pages = [pg for pg in browser.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url]
    page = task_pages[0]

    # Find React Fiber containing transcript
    data = await page.evaluate('''() => {
        // Look for transcript in DOM / React fiber
        function findReactProp(root, propName, maxDepth = 20) {
            const visited = new Set();
            function walk(node, depth) {
                if (!node || depth > maxDepth || visited.has(node)) return null;
                visited.add(node);

                if (node.memoizedProps && node.memoizedProps[propName]) {
                    return node.memoizedProps[propName];
                }
                if (node.stateNode && node.stateNode[propName]) {
                    return node.stateNode[propName];
                }
                if (node.memoizedState) {
                    let s = node.memoizedState;
                    while (s) {
                        if (s.memoizedState && s.memoizedState[propName]) return s.memoizedState[propName];
                        s = s.next;
                    }
                }

                // Check child and sibling
                if (node.child) {
                    const res = walk(node.child, depth + 1);
                    if (res) return res;
                }
                if (node.sibling) {
                    const res = walk(node.sibling, depth + 1);
                    if (res) return res;
                }
                return null;
            }
            return walk(root, 0);
        }

        // Find root fiber
        const el = document.querySelector('#root, #__next, div[data-reactroot], body');
        let fiber = null;
        for (const k in el) {
            if (k.startsWith('__reactFiber') || k.startsWith('__reactInternalInstance')) {
                fiber = el[k];
                break;
            }
        }

        // Search for steps or transcript in window or React fibers
        let found = null;
        // Search through all elements for __reactFiber
        const allEls = document.querySelectorAll('*');
        for (const elem of allEls) {
            for (const k in elem) {
                if (k.startsWith('__reactFiber')) {
                    const f = elem[k];
                    const props = f?.memoizedProps || {};
                    if (props.steps || props.messages || props.trajectory || props.transcript) {
                        return {
                            type: 'element_prop',
                            keys: Object.keys(props),
                            stepCount: props.steps ? props.steps.length : (props.messages ? props.messages.length : 0),
                            sample: props.steps ? props.steps.slice(0, 3) : null
                        };
                    }
                }
            }
        }
        return { not_found: true };
    }''')

    print("React Fiber search result:")
    print(json.dumps(data, indent=2, default=str))

    await p.stop()

if __name__ == '__main__':
    asyncio.run(extract_transcript_from_react())
