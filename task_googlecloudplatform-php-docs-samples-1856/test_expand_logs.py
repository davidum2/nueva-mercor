import asyncio
from playwright.async_api import async_playwright

async def expand_logs():
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [pg for ctx in browser.contexts for pg in ctx.pages if 'task_a6c04444' in pg.url and 'sign-in' not in pg.url][0]
    
    res = await page.evaluate('''() => {
        const triggers = Array.from(document.querySelectorAll('button[data-slot="collapsible-trigger"]'));
        const logsTrigger = triggers.find(b => (b.innerText || '').includes('LOGS'));
        if (!logsTrigger) return 'LOGS trigger button not found';
        logsTrigger.click();
        return 'Clicked LOGS trigger button! State: ' + logsTrigger.getAttribute('data-state');
    }''')
    print(res)
    await asyncio.sleep(2.0)
    
    info = await page.evaluate('''() => {
        const text = document.body.innerText;
        const btns = Array.from(document.querySelectorAll('button')).map(b => (b.innerText || '').trim()).filter(t => t.length > 0);
        const hasStep = text.includes('Step 1');
        const expandBtn = btns.find(t => t.includes('Expand all') || t.includes('Collapse all'));
        return { hasStep, expandBtn, totalButtons: btns.length, textLen: text.length };
    }''')
    print('After expanding collapsible:', info)

    # Click Expand all if present
    clicked_exp = await page.evaluate('''() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const exp = btns.find(b => (b.innerText || '').trim() === 'Expand all');
        if (exp) {
            exp.click();
            return true;
        }
        return false;
    }''')
    print('Clicked Expand all:', clicked_exp)
    await asyncio.sleep(2.0)

    # Count more lines buttons
    more_count = await page.evaluate('''() => {
        const btns = Array.from(document.querySelectorAll('button')).filter(b => {
            const t = (b.innerText || '').toLowerCase();
            return t.includes('more lines') || t.includes('show more');
        });
        return btns.length;
    }''')
    print('More lines buttons count:', more_count)

    await browser.close()
    await p.stop()

if __name__ == '__main__':
    asyncio.run(expand_logs())
