import asyncio
import json
from playwright.async_api import async_playwright

async def main():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [p for ctx in browser.contexts for p in ctx.pages if 'mercor.com' in p.url][0]

    fiber_data = await page.evaluate('''() => {
        // Find element containing Trajectory Viewer or Model A
        const elements = Array.from(document.querySelectorAll('*'));
        
        function findReactProps(el) {
            const key = Object.keys(el).find(k => k.startsWith('__reactProps$') || k.startsWith('__reactFiber$'));
            return key ? el[key] : null;
        }

        let found = [];
        for (let el of elements) {
            const fiber = findReactProps(el);
            if (!fiber) continue;

            // Search fiber / memoizedProps for keywords like steps, rollout, trajectory, diff
            let curr = fiber;
            let depth = 0;
            while (curr && depth < 20) {
                const props = curr.memoizedProps || curr;
                if (props) {
                    if (props.rollout || props.trajectory || props.steps || props.modelA || props.modelB || props.taskData) {
                        return {
                            hasRollout: !!props.rollout,
                            hasTrajectory: !!props.trajectory,
                            hasSteps: !!props.steps,
                            keys: Object.keys(props),
                            rolloutKeys: props.rollout ? Object.keys(props.rollout) : null,
                            trajectoryKeys: props.trajectory ? Object.keys(props.trajectory) : null,
                            stepsCount: props.steps ? props.steps.length : (props.trajectory?.steps ? props.trajectory.steps.length : null)
                        };
                    }
                }
                curr = curr.return;
                depth++;
            }
        }
        return { message: "No direct props found via simple loop" };
    }''')
    print('Fiber inspect result:', fiber_data)

if __name__ == "__main__":
    asyncio.run(main())
