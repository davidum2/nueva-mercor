import asyncio
import os
import json
from playwright.async_api import async_playwright

TASK_ID = "task_74b080f5a1554daaba2595c070f210f7"
OUTPUT_DIR = os.path.join(os.getcwd(), TASK_ID)

async def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    
    target_page = None
    for ctx in browser.contexts:
        for page in ctx.pages:
            if TASK_ID in page.url or 'mercor.com' in page.url:
                target_page = page
                break
        if target_page:
            break
            
    if not target_page:
        print("No se encontro la pagina de la tarea.")
        return

    print(f"Conectado a: {target_page.url}")
    
    # 1. Extraer innerText completo
    full_text = await target_page.evaluate('document.body.innerText')
    with open(os.path.join(OUTPUT_DIR, "page_raw_text.txt"), "w", encoding="utf-8") as f:
        f.write(full_text)
    print(f"Texto guardado en page_raw_text.txt ({len(full_text)} caracteres)")

    # 2. Extraer HTML completo
    html_content = await target_page.content()
    with open(os.path.join(OUTPUT_DIR, "page_full.html"), "w", encoding="utf-8") as f:
        f.write(html_content)
    print("HTML completo guardado en page_full.html")

    # 3. Extraer información estructurada (títulos, encabezados, botones, tabs)
    metadata = await target_page.evaluate('''() => {
        const headings = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, h6')).map(h => ({
            tag: h.tagName,
            text: h.innerText.trim()
        }));
        
        const tabs = Array.from(document.querySelectorAll('[role="tab"], button')).map(b => b.innerText.trim()).filter(Boolean);
        
        const textareas = Array.from(document.querySelectorAll('textarea')).map((t, idx) => ({
            index: idx,
            placeholder: t.placeholder,
            name: t.name,
            id: t.id,
            valueLength: t.value.length,
            valuePreview: t.value.substring(0, 100)
        }));

        return {
            title: document.title,
            url: window.location.href,
            headings,
            textareasCount: textareas.length,
            textareas
        };
    }''')

    with open(os.path.join(OUTPUT_DIR, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    print("Metadatos guardados en metadata.json")

    # 4. Intentar capturar estado de React o props si es accesible en window / __NEXT_DATA__
    next_data = await target_page.evaluate('''() => {
        if (window.__NEXT_DATA__) return window.__NEXT_DATA__;
        return null;
    }''')
    if next_data:
        with open(os.path.join(OUTPUT_DIR, "next_data.json"), "w", encoding="utf-8") as f:
            json.dump(next_data, f, indent=2, ensure_ascii=False)
        print("Datos de __NEXT_DATA__ guardados.")

    # 5. Tomar captura de pantalla
    screenshot_path = os.path.join(OUTPUT_DIR, "task_screenshot.png")
    await target_page.screenshot(path=screenshot_path, full_page=False)
    print(f"Captura guardada en {screenshot_path}")

    # Cerrar conexion CDP limpiamente
    # No cerrar browser para no cerrar Comet
    
if __name__ == "__main__":
    asyncio.run(main())
