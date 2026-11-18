import asyncio
from playwright.async_api import async_playwright

async def inspect_traj():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = browser.contexts[0].pages[0]

    # Navigate to Trajectory Viewer
    await page.evaluate("""() => {
        const btns = Array.from(document.querySelectorAll('button, li button, [role="tab"]'));
        const tv = btns.find(b => (b.innerText || '').trim() === 'Trajectory Viewer');
        if (tv) tv.click();
    }""")
    await asyncio.sleep(1.5)

    data = await page.evaluate("""() => {
        // Find elements with text containing 'Step 1' or 'Step 2'
        const steps = Array.from(document.querySelectorAll('*')).filter(el => {
            const t = (el.innerText || '').trim();
            return /^Step \d+/.test(t) && el.children.length === 0;
        });

        // Find the container for these steps
        let container = null;
        if (steps.length > 0) {
            let p = steps[0].parentElement;
            while (p && p.tagName !== 'BODY') {
                if (p.children.length > 5) {
                    container = {
                        tag: p.tagName,
                        className: p.className,
                        childrenCount: p.children.length,
                        innerTextSample: p.innerText.slice(0, 500)
                    };
                    break;
                }
                p = p.parentElement;
            }
        }

        return {
            stepsFound: steps.length,
            firstFewSteps: steps.slice(0, 5).map(s => s.innerText.trim()),
            container
        };
    }""")

    print("Trajectory inspection:")
    print("Steps count found:", data['stepsFound'])
    print("First few steps:", data['firstFewSteps'])
    if data['container']:
        print("Container tag:", data['container']['tag'])
        print("Container children:", data['container']['childrenCount'])
        print("Sample text:\n", data['container']['innerTextSample'][:300])

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(inspect_traj())
