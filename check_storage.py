import asyncio
import json
from playwright.async_api import async_playwright

async def main():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [p for ctx in browser.contexts for p in ctx.pages if 'mercor.com' in p.url][0]

    storage_data = await page.evaluate('''() => {
        const local = {};
        for (let i = 0; i < localStorage.length; i++) {
            const k = localStorage.key(i);
            local[k] = localStorage.getItem(k)?.substring(0, 500);
        }
        const session = {};
        for (let i = 0; i < sessionStorage.length; i++) {
            const k = sessionStorage.key(i);
            session[k] = sessionStorage.getItem(k)?.substring(0, 500);
        }
        return { local, session };
    }''')

    with open('task_74b080f5a1554daaba2595c070f210f7/storage_dump.json', 'w', encoding='utf-8') as f:
        json.dump(storage_data, f, indent=2)
    print("Storage guardado.")

if __name__ == "__main__":
    asyncio.run(main())
