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

    form_info = await mercor_page.evaluate("""() => {
        // Find any element with react hook form or form values
        const allElements = Array.from(document.querySelectorAll('*'));
        for (const el of allElements) {
            const key = Object.keys(el).find(k => k.startsWith('__reactFiber$'));
            if (!key) continue;
            let f = el[key];
            while (f) {
                if (f.memoizedProps && f.memoizedProps.register) {
                    return {
                        hasRegister: true,
                        formValues: f.memoizedProps.getValues ? f.memoizedProps.getValues() : null
                    };
                }
                if (f.memoizedState && f.memoizedState.memoizedState && typeof f.memoizedState.memoizedState === 'object') {
                    const s = f.memoizedState.memoizedState;
                    if (s.field_ta_rubric_01_answer_a || s.field_ta_rubric_02_answer_a) {
                        return {
                            foundInState: true,
                            keys: Object.keys(s)
                        };
                    }
                }
                f = f.return;
            }
        }
        return { notFound: true };
    }""")
    print("Form info:", form_info)

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
