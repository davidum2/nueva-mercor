import asyncio
from playwright.async_api import async_playwright

async def find_rubric_a():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page0 = browser.contexts[0].pages[0]

    res = await page0.evaluate("""() => {
        const allElements = Array.from(document.querySelectorAll('*'));
        const matches = [];
        for (const el of allElements) {
            const text = el.innerText || '';
            if (text.includes('answer (A)') || text.includes('reason (A)')) {
                // If it's a leaf or small element
                if (el.children.length <= 2) {
                    matches.push({
                        tag: el.tagName,
                        className: el.className,
                        text: text.slice(0, 100).split('\\n').join(' ')
                    });
                }
            }
        }
        return matches;
    }""")

    print(f"Matches for 'answer (A)' or 'reason (A)' on Page 0: {len(res)}")
    for m in res[:20]:
        print(" ", m)

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(find_rubric_a())
