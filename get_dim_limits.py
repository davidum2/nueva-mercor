import asyncio
import json
from playwright.async_api import async_playwright

TASK_ID = 'task_08ccf272669347c3af63de71b2ecb5e5'

async def get_dim_limits():
    p = await async_playwright().start()
    b = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [pg for pg in b.contexts[0].pages if TASK_ID in pg.url and 'sign-in' not in pg.url and 'rubric' not in pg.url][0]

    limits = await page.evaluate('''() => {
        const labels = Array.from(document.querySelectorAll('label, div, p')).filter(el => {
            const t = el.innerText || '';
            return t.includes('characters') || t.includes('Length') || t.includes('min') || t.includes('max');
        });
        return labels.map(l => l.innerText.trim()).filter(t => t.length < 150);
    }''')
    print('Limits text found:', limits[:20])

    # Check textarea containers
    ta_info = await page.evaluate('''() => {
        const tas = Array.from(document.querySelectorAll('textarea'));
        return tas.map(t => ({
            name: t.name,
            placeholder: t.placeholder,
            id: t.id,
            minLength: t.minLength,
            maxLength: t.maxLength
        }));
    }''')
    print('Textareas:', json.dumps(ta_info[:10], indent=2))

    await b.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(get_dim_limits())
