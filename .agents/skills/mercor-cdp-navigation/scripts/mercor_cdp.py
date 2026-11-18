"""
Mercor CDP Automation Helpers
Módulo de utilidades para interactuar con Mercor Studio vía CDP (puerto 9223).
"""
import asyncio
from playwright.async_api import async_playwright

async def get_mercor_page(port: int = 9223):
    """Conecta por CDP a Comet y busca la pestaña activa de Mercor."""
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp(f'http://127.0.0.1:{port}')
    mercor_page = None
    for ctx in browser.contexts:
        for page in ctx.pages:
            if 'mercor.com' in page.url:
                mercor_page = page
                break
        if mercor_page:
            break
    return browser, mercor_page

async def check_autoqc(page):
    """Monitorea el estado de las pruebas AutoQC en tiempo real."""
    text = await page.evaluate('document.body.innerText')
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    status_lines = [l for l in lines if any(k in l for k in ['AutoQC', '17', 'Pass', 'Fail', 'Warnings', 'Running'])]
    return status_lines

async def set_react_textarea_value(page, selector_or_index: int, value: str):
    """
    Inyecta texto en un textarea controlado por React usando el native prototype descriptor.
    """
    js_code = """
    ([idx, nuevoTexto]) => {
        const textareas = document.querySelectorAll('textarea');
        const element = textareas[idx];
        if (!element) return false;
        
        const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
            window.HTMLTextAreaElement.prototype, "value"
        ).set;
        nativeInputValueSetter.call(element, nuevoTexto);
        element.dispatchEvent(new Event('input', { bubbles: true }));
        element.dispatchEvent(new Event('change', { bubbles: true }));
        return true;
    }
    """
    return await page.evaluate(js_code, [selector_or_index, value])
