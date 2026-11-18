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

    # Click Model A tab in the right sidebar or find Model A tab
    res = await mercor_page.evaluate("""() => {
        const tabs = Array.from(document.querySelectorAll('[role="tab"]'));
        const modelATab = tabs.find(t => t.innerText.trim() === 'Model A');
        const modelBTab = tabs.find(t => t.innerText.trim() === 'Model B');
        
        return {
            hasModelA: !!modelATab,
            hasModelB: !!modelBTab,
            modelASelected: modelATab?.getAttribute('aria-selected'),
            modelBSelected: modelBTab?.getAttribute('aria-selected')
        };
    }""")
    print("Tabs status:", res)

    # Let's search all elements containing 'answer (A)' or 'answer (B)'
    ans_info = await mercor_page.evaluate("""() => {
        const els = Array.from(document.querySelectorAll('*'));
        const aAnswers = [];
        const bAnswers = [];
        for (const el of els) {
            const txt = (el.innerText || '').trim();
            if (txt.includes('Rubric') && txt.includes('answer (A)')) {
                aAnswers.push({ text: txt.slice(0, 60), tag: el.tagName });
            }
            if (txt.includes('Rubric') && txt.includes('answer (B)')) {
                bAnswers.push({ text: txt.slice(0, 60), tag: el.tagName });
            }
        }
        return { aCount: aAnswers.length, bCount: bAnswers.length, aSample: aAnswers.slice(0, 5), bSample: bAnswers.slice(0, 5) };
    }""")
    print("Answers info:", json.dumps(ans_info, indent=2))

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(run())
