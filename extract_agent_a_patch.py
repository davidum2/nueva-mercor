import asyncio
import os
from playwright.async_api import async_playwright

async def main():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [p for ctx in browser.contexts for p in ctx.pages if 'mercor.com' in p.url][0]

    # Click on agent.patch in the diff list
    clicked = await page.evaluate('''() => {
        const els = Array.from(document.querySelectorAll('*'));
        const patchEl = els.find(el => el.innerText && el.innerText.trim() === 'agent.patch');
        if (patchEl) {
            patchEl.click();
            return true;
        }
        return false;
    }''')
    print("Clicked agent.patch:", clicked)
    await asyncio.sleep(2.0)

    # Read Monaco model
    content = await page.evaluate('''() => {
        const monaco = window.monaco;
        if (monaco && monaco.editor) {
            const models = monaco.editor.getModels();
            // Find model with agent.patch or longest model
            for (let m of models) {
                if (m.uri.toString().includes('agent.patch')) {
                    return m.getValue();
                }
            }
            return models[models.length - 1].getValue();
        }
        return null;
    }''')

    if content:
        out_path = 'task_74b080f5a1554daaba2595c070f210f7/model_a/agent_a.patch'
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Saved agent_a.patch ({len(content)} bytes)")
    else:
        print("Could not get agent_a.patch content")

if __name__ == "__main__":
    asyncio.run(main())
