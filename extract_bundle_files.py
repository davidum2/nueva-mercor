import asyncio
import os
import json
from playwright.async_api import async_playwright

TASK_ID = "task_74b080f5a1554daaba2595c070f210f7"
OUTPUT_DIR = os.path.join(os.getcwd(), TASK_ID)
BUNDLE_DIR = os.path.join(OUTPUT_DIR, "bundle")

FILES_TO_EXTRACT = [
    "Dockerfile",
    "golden.patch",
    "solve.sh",
    "config.json",
    "grade.py",
    "test.patch",
    "test.sh",
    "instruction.md",
    "task.toml"
]

async def main():
    os.makedirs(BUNDLE_DIR, exist_ok=True)
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [p for ctx in browser.contexts for p in ctx.pages if 'mercor.com' in p.url][0]

    # Extract all files from bundle explorer
    for filename in FILES_TO_EXTRACT:
        print(f"Buscando y abriendo: {filename}...")
        # Find the button containing this exact filename
        button_clicked = await page.evaluate(f'''(fname) => {{
            const buttons = Array.from(document.querySelectorAll('button'));
            const target = buttons.find(b => b.innerText.trim() === fname);
            if (target) {{
                target.click();
                return true;
            }}
            return false;
        }}''', filename)

        if button_clicked:
            await asyncio.sleep(1.2)
            content = await page.evaluate('''() => {
                if (window.monaco && window.monaco.editor) {
                    const models = window.monaco.editor.getModels();
                    if (models.length > 0) {
                        return models[models.length - 1].getValue();
                    }
                }
                const editorEl = document.querySelector('.monaco-editor');
                if (editorEl) return editorEl.innerText;
                const pre = document.querySelector('pre');
                if (pre) return pre.innerText;
                return null;
            }''')
            
            if content is not None:
                file_path = os.path.join(BUNDLE_DIR, filename)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"  -> Guardado {filename} ({len(content)} bytes)")
            else:
                print(f"  -> No se pudo obtener contenido para {filename}")
        else:
            print(f"  -> Boton para {filename} no encontrado.")

    # Ahora expandir 'Show more' en Prompt y Final Answer
    print("\nExtrayendo Prompt completo y Final Answer de Model A...")
    prompt_data = await page.evaluate('''() => {
        // Buscar botones Show more
        const showMoreButtons = Array.from(document.querySelectorAll('button')).filter(b => b.innerText.includes('Show more'));
        showMoreButtons.forEach(b => b.click());
    }''')
    await asyncio.sleep(1.0)
    
    # Extraer prompt y final answer de Model A
    model_a_data = await page.evaluate('''() => {
        // Encontrar sección de prompt
        let promptText = "";
        let finalAnswerText = "";
        
        const allText = document.body.innerText;
        return {
            fullText: allText
        };
    }''')

if __name__ == "__main__":
    asyncio.run(main())
