---
name: mercor-cdp-navigation
description: >-
  Navegación, inspección, automatización y llenado de formularios en Mercor Studio mediante Chrome DevTools Protocol (CDP) sobre el puerto 9223 en el navegador Comet. Usar cuando se interactúe con Mercor Studio, se auditen pruebas de AutoQC o se manipulen textareas de rúbricas y dimensiones de forma segura sin disparar bloqueos.
---

# GUÍA DE NAVEGACIÓN Y AUTOMATIZACIÓN EN MERCOR STUDIO (VÍA CDP)
**Módulo:** Skill de Navegación del Asistente  
**Método:** Chrome DevTools Protocol (CDP) sobre puerto `9223` (Navegador Comet)  
**Objetivo:** Conectar, inspeccionar, rellenar y auditar tareas en Mercor Studio de forma segura y sin disparar bloqueos de seguridad.

---

## 1. REGLAS DE ORO DE CONEXIÓN

1. **Conexión obligatoria por CDP:**  
   Conectarse siempre a la sesión activa en `http://127.0.0.1:9223` o `http://localhost:9223`.  
   *Nunca* abrir una instancia separada o nueva de Chrome/Playwright autónomo, ya que se perderían las sesiones de Okta SSO, las cookies de Mercor y se detonarían los bloqueos de Cloudflare.

   **Comandos para abrir Comet en modo depuración (puerto 9223):**
   * **Vía script directo (.bat):**
     ```cmd
     iniciar_comet.bat
     ```
   * **Vía PowerShell:**
     ```powershell
     Start-Process "$env:LOCALAPPDATA\Perplexity\Comet\Application\comet.exe" -ArgumentList "--remote-debugging-port=9223"
     ```
   * **Verificar si el puerto 9223 está activo:**
     ```powershell
     Test-NetConnection -ComputerName 127.0.0.1 -Port 9223
     ```
   * *Nota crítica:* Si Comet ya estaba abierto normalmente (sin el flag), Chromium ignora el parámetro. Debe cerrarse primero (`taskkill /IM comet.exe` o cerrar ventana) y abrirse de nuevo con el comando de depuración.

2. **Reutilizar pestañas abiertas:**  
   Buscar la pestaña que contenga `mercor.com` en su URL antes de crear una nueva.

3. **Inyección compatible con React 16+:**  
   En Mercor Studio los formularios utilizan componentes controlados por React. Modificar la propiedad `value` de un elemento directamente no actualiza el estado interno de React. Para forzar la actualización, se debe usar el *native prototype descriptor*:
   ```javascript
   const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
       window.HTMLTextAreaElement.prototype, "value"
   ).set;
   nativeInputValueSetter.call(element, nuevoTexto);
   element.dispatchEvent(new Event('input', { bubbles: true }));
   element.dispatchEvent(new Event('change', { bubbles: true }));
   ```

---

## 2. SCRIPTS Y PATRONES DE NAVEGACIÓN PROBADOS

### A. Conexión Básica y Búsqueda de Pestaña de Mercor
```python
import asyncio
from playwright.async_api import async_playwright

async def get_mercor_page():
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
    return browser, mercor_page
```

---

### B. Inspección del Estado de AutoQC en Tiempo Real
Para monitorear el progreso de las 17 pruebas sin interferir con la pantalla:
```python
async def check_autoqc(page):
    text = await page.evaluate('document.body.innerText')
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    
    # Extraer líneas clave de estado
    status_lines = [l for l in lines if any(k in l for k in ['AutoQC', '17', 'Pass', 'Fail', 'Warnings', 'Running'])]
    return status_lines
```

---

### C. Mapeo Seguro de Textareas (Rúbricas vs. Dimensiones)
El formulario de Mercor Studio organiza las casillas de texto en un orden indexado exacto:

| Índices en DOM | Sección en la Plataforma | Contenido que Debe Recibir |
|:---:|---|---|
| **`idx: 1 a 8`** | **Dimensiones 2 a 9 (Lado A)** | Evaluaciones conceptuales (diff shape, telescoping, test integrity). |
| **`idx: 9 a 16`** | **Rúbricas 1 a 8 (Lado A)** | Respuestas directas a la pregunta técnica de cada rúbrica. |
| **`idx: 24 a 31`** | **Dimensiones 2 a 9 (Lado B)** | Evaluaciones conceptuales del Lado B. |
| **`idx: 32 a 39`** | **Rúbricas 1 a 8 (Lado B)** | Respuestas directas a la pregunta de cada rúbrica para el Lado B. |
| **`idx: 47`** | **Comparative Rationale (Tab F)** | Veredicto comparativo de 3 párrafos (850 a 1,000 caracteres). |

---

### D. Reejecución Focalizada de Pruebas Observadas (*Rerun Selected*)
Cuando AutoQC marca una advertencia o fallo en una prueba específica, no es necesario reevaluar las 17 completas (lo que tomaría 15 minutos). Se puede reevaluar únicamente la fallida en 30 a 60 segundos:
1. Localizar el checkbox con `aria-label*="[Nombre de la prueba]"`.
2. Hacer clic en el checkbox.
3. Hacer clic en el botón `Rerun 1 selected`.

---

## 3. PROTOCOLO DE HUMANIZACIÓN Y SEGURIDAD

* **Respeto a la Acción Final del Usuario:** Aunque el llenado y la corrección técnica de textos se ejecute automáticamente vía CDP, el clic final de entrega (**`Submit review`**) o la confirmación de la misma debe ser validada visualmente por el usuario con su contador de Insightful activo.
* **Tiempos de Espera Naturales:** Introducir pausas de 500ms a 1000ms entre eventos de teclado o clics para reflejar un comportamiento humano ante cualquier auditoría de traza web.
