---
name: php-dlp-trajectory-evaluator
description: Auditoría, extracción y evaluación técnica de trayectorias en SWE-bench para tareas de PHP y Google Cloud DLP en Mercor Studio. Incluye reglas de evaluación objetiva, detección de contratos de API, análisis de mocks en pruebas unitarias y calibración de rúbricas con tasa de YES < 75% para Gemini.
---

# PHP DLP Trajectory Evaluator Skill

Este skill proporciona la metodología, reglas técnicas y herramientas automatizadas para auditar, extraer y evaluar trayectorias de agentes (SWE-bench / OpenCode) en tareas de PHP y SDKs de Google Cloud, específicamente Google Cloud Data Loss Prevention (DLP).

---

## 1. Reglas Técnicas y Primitivas de Evaluación

### 1.1 Entorno de Ejecución PHP 8
- **Cumplimiento Estricto de Firmas:** En PHP 8+, invocar una función con menos argumentos de los requeridos (parámetros no opcionales sin valor por defecto) lanza un error fatal fatal `ArgumentCountError` no capturado.
- **Detección de Parámetros Extraños:** Si un modelo agrega parámetros intermedios no solicitados en la firma pública requerida, rompe cualquier caller downstream y el arnés de pruebas (por ejemplo, `dlpTest.php` pasa exactamente 8 argumentos).
- **Manejo de Recursos (gRPC/HTTP):** Los clientes de Google Cloud como `DlpServiceClient` deben cerrarse mediante `$dlp->close()` en un bloque `finally` para liberar recursos y sockets.

### 1.2 Integración con Google Cloud DLP SDK
- **Configuración de Almacenamiento GCS:**
  ```php
  $cloudStorageOptions = (new CloudStorageOptions())
      ->setFileSet((new FileSet())->setUrl($inputGcsPath));
  $storageConfig = (new StorageConfig())
      ->setCloudStorageOptions($cloudStorageOptions);
  ```
- **Resolución de Nombres de Plantillas:**
  El SDK de Google Cloud DLP exige nombres de recurso calificados (`projects/{project}/locations/{loc}/deidentifyTemplates/{name}`). Las implementaciones canónicas usan:
  ```php
  DlpServiceBaseClient::projectDeidentifyTemplateName($callingProjectId, $templateName);
  ```
  Pasar strings crudos puede fallar en llamadas reales si el backend requiere el URI canónico.
- **Inspección de Configuración (`InspectJobConfig`):**
  Un trabajo de inspección y desidentificación requiere asociar tanto `$storageConfig` como `$inspectConfig` (con `infoTypes` como `PERSON_NAME`, `EMAIL_ADDRESS`) y el array de acciones `$actions`. Omitir `setInspectConfig` es un defecto estructural de arquitectura.
- **Tipos de Archivo a Transformar:**
  La acción `Deidentify` debe especificar explícitamente qué tipos de archivo procesar vía `setFileTypesToTransform([FileType::TEXT_FILE, FileType::IMAGE, FileType::CSV])`.

### 1.3 Análisis de Arneses de Prueba y Mocks (Prophecy / PHPUnit)
- En repositorios de Google Cloud Samples (`GoogleCloudPlatform/php-docs-samples`), los tests a menudo usan sustitución por expresiones regulares del cliente en archivos temporales:
  ```php
  $fileContent = preg_replace('/\$dlp\s*=\s*new\s+DlpServiceClient\s*\(\s*\)\s*;/', 'global $dlp;', $fileContent);
  ```
- Si el modelo instancia el cliente con una sintaxis no estándar o renombra la variable a `$client`, el mock global falla y el test intenta conectar a la red en vivo, fallando.

---

## 2. Directrices de Calibración de Rúbricas Mercor AutoQC

### 2.1 Regla Matemática de Tasa de Aprobación de Gemini
- **Requisito Mandatorio:** La tasa de `YES` para el lado de Gemini (Model A) debe ser **estrictamente menor al 75%** (`< 75%`).
- **Tabla de Calibración:**
  - 10 Rúbricas: 6 ó 7 YES para Model A (60.0% – 70.0% YES) -> **VÁLIDO**
  - 12 Rúbricas: 8 YES para Model A (66.7% YES) -> **ÓPTIMO**
  - 13 Rúbricas: 9 YES para Model A (69.2% YES) -> **ÓPTIMO**
  - 14 Rúbricas: 9 ó 10 YES para Model A (64.3% – 71.4% YES) -> **ÓPTIMO**
  - 15 Rúbricas: 10 ó 11 YES para Model A (66.7% – 73.3% YES) -> **VÁLIDO**

### 2.2 Política Estricta Anti-LLM Slop
- Prohibido el uso de lenguaje genérico ("The model did an excellent job", "implemented robustly").
- Cada razón debe citar:
  1. El archivo exacto (`dlp/src/deidentify_cloud_storage.php`).
  2. La línea de diff específica (`patch_a.diff:L81-84`, `patch_b.diff:L60-70`).
  3. Los nombres exactos de funciones, métodos o llamadas de API (`setInspectConfig`, `ArgumentCountError`, `setFileTypesToTransform`).
  4. En dimensiones de proceso (6 y 7), citar el número de paso de la trayectoria (`Step 34: php -l`).

---

## 3. Flujo de Evaluación de Trayectorias

1. **Extracción:** Parsear los pasos de la trayectoria desde los archivos de texto expandido o el árbol fiber en `steps_structured.json`.
2. **Generación del Banco de Preguntas:** Crear 50 preguntas atómicas (Noul style, YES = good) repartidas en Dimensiones 2 a 9.
3. **Evaluación 50x2:** Evaluar Model A y Model B contra cada una de las 50 preguntas con veredictos fundamentados.
4. **Filtrado y Selección:** Elegir entre 12 y 14 rúbricas asegurando que Model A cumpla `< 75% YES`.
5. **Generación de Reportes:** Producir matrices de evidencia y justificaciones de texto formateadas.
