import asyncio
from playwright.async_api import async_playwright

async def main():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [p for ctx in browser.contexts for p in ctx.pages if 'mercor.com' in p.url][0]

    # Ensure Model A is selected in Trajectory Viewer
    await page.locator('button').filter(has_text="Model A").first.click()
    await asyncio.sleep(1.0)

    # Click DIFF tab
    print("Clicking DIFF tab in Trajectory Viewer...")
    await page.locator('button').filter(has_text="DIFF").first.click()
    await asyncio.sleep(2.0)

    # Check Monaco models or diff viewer
    diff_data = await page.evaluate('''() => {
        const monaco = window.monaco;
        let modelsInfo = [];
        if (monaco && monaco.editor) {
            const models = monaco.editor.getModels();
            modelsInfo = models.map(m => ({
                uri: m.uri.toString(),
                len: m.getValue().length,
                preview: m.getValue().substring(0, 100)
            }));
        }

        // Also check any file list in DIFF viewer
        const fileList = Array.from(document.querySelectorAll('button, div, span, a')).filter(el => {
            return el.innerText && (el.innerText.endsWith('.java') || el.innerText.endsWith('.proto') || el.innerText.endsWith('.sh'));
        }).map(el => el.innerText.trim());

        return {
            modelsCount: modelsInfo.length,
            models: modelsInfo,
            fileList: Array.from(new Set(fileList))
        };
    }''')

    print("Diff data:", diff_data)

if __name__ == "__main__":
    asyncio.run(main())
