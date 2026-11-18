# GUÍA MAESTRA: COMPRENSIÓN PROFUNDA DE LA TAREA MERCOR STUDIO
**ID de la Tarea:** `task_74b080f5a1554daaba2595c070f210f7`  
**Título del Task:** `bazelbuild-bazel-21177 [model A/B]`  
**Proyecto:** Project Anton | SWE Trajectory QC Annotation  
**Campaña:** `camp_75099d23386f4394ab7596a5ea538da8`  
**Estado:** *Annotating* (Needs attention from `[EXP] Edgar D`)  

---

## 1. RESUMEN EJECUTIVO Y OBJETIVO DE LA TAREA

En esta tarea de **Project Anton**, tu rol **no es programar desde cero**, sino actuar como **Juez y Evaluador Experto de Control de Calidad (QC)** sobre las trayectorias de dos agentes de inteligencia artificial (**Model A** y **Model B**).

Ambos modelos recibieron un problema de ingeniería de software real del repositorio **`bazelbuild/bazel`** (Issue #21177, commit base `3f11b34`, versión 7.1.0). Tu objetivo es:
1. Analizar el problema técnico de Bazel y su solución canónica (`golden.patch`).
2. Auditar paso a paso la ejecución y el diff generado por el **Model A** (108 pasos, 15 archivos modificados, +690/-57).
3. Auditar paso a paso la ejecución y el diff generado por el **Model B** (66 pasos, 7 archivos modificados, +20/-13).
4. Calificar las **Dimensiones 2 a 9** para ambos modelos con evidencias concretas (pasos, archivos, líneas de código).
5. Completar y justificar las **Rúbricas Binarias** (entre 8 y 15 preguntas Sí/No donde SÍ es siempre positivo).
6. Emitir un **Veredicto Comparativo (Pairwise Verdict)** con una justificación de 3 párrafos (~850-1000 caracteres) coherente con las notas.
7. Corregir y pasar las **17 validaciones de AutoQC** para enviar la tarea a revisión final.

---

## 2. ANÁLISIS TÉCNICO DEL PROBLEMA EN BAZEL (#21177)

### El Problema (instruction.md):
El registro de ejecución de spawns de Bazel (`spawn execution log`), implementado en `CompactSpawnLogContext.java` y `ExpandedSpawnLogContext.java` junto con el protocolo `spawn.proto`, presentaba **tres deficiencias críticas**:

1. **Salidas de enlaces simbólicos no resueltos (Unresolved symlinks):**  
   Cuando una acción de compilación declara un symlink como salida, el logger lo trataba erróneamente como un archivo faltante (`missing_path`), perdiendo completamente la ruta de destino (`target path`) del symlink.
   * *Solución esperada:* En `spawn.proto`, agregar el campo `symlink_target_path` en `File` y `ExecLogEntry.File`, y en el formato compacto registrar un `unresolved_symlink_id`.

2. **Falta de distinción entre tipo de archivo incorrecto y salida ausente:**  
   Si una salida se declaraba como archivo pero en disco resultaba ser un directorio (o viceversa), el sistema lo agrupaba ciegamente en `missing_path`.
   * *Solución esperada:* Separar las salidas con discrepancia de tipo mediante un campo dedicado (`invalid_output_path` o `invalid_path`) para que los desarrolladores puedan diagnosticar incompatibilidades de tipos.

3. **Salidas indirectas a través de symlinks no seguidas:**  
   Si una salida declarada como archivo o directorio era en realidad un symlink intermedio que apuntaba al archivo/directorio real en otra ubicación, el logger no seguía el enlace para calcular su digest (hash) o listar el directorio.
   * *Solución esperada:* Seguir transparentemente el enlace simbólico para obtener el contenido real.

### Clasificación en `task.toml`:
* **Category:** `Debugging and Repair`
* **Subcategory:** `Runtime bug repair`
* **Dificultad:** Medium (Pass@8 en Opus 4.8: 3/8)

---

## 3. COMPARATIVA TÉCNICA: MODELO A vs. MODELO B

| Criterio | Modelo A (Trajectory A) | Modelo B (Trajectory B) |
|---|---|---|
| **Número de Pasos** | 108 pasos | 66 pasos (más directo y eficiente) |
| **Volumen de Diff** | 15 archivos (+690 / -57) | 7 archivos (+20 / -13, quirúrgico) |
| **Manejo de Protos** | Modificó múltiples mensajes en `spawn.proto`, creando campos adicionales. | Modificó estrictamente lo necesario en `spawn.proto`. |
| **Pruebas y Tests** | Agregó pruebas extensas pero con mayor dispersión. | Sustituyó `testDirectoryOutput` por `testFileOutput_wrongType` en el paso 39 y verificó en paso 61. |
| **Debilidades Compartidas** | Ambos conservaron `missing_path` junto al nuevo campo de tipo incorrecto, dejando categorías que la reconstrucción de tests no maneja de forma ideal. | Ambos tienen áreas de mejora en la cobertura estricta de proto reconstruction. |

---

## 4. ESTRUCTURA Y FLUJO DE TRABAJO (TABS A - H)

### Tab A: How this task works
Instrucciones generales del flujo de anotación. Regla fundamental: Trabajar las pestañas en orden y calibrar las justificaciones con citas precisas.

### Tab B: Task bundle
Explorador de archivos del entorno.
* **Acción requerida:** Clasificar el **Task type** en el dropdown seleccionando `Debugging and Repair` / `Runtime bug repair` conforme a `task.toml`.

### Tab C: Agent solution A (Calificación Dimensiones 2-9)
Calificar en escala de 1 a 5 con justificaciones de más de 15 palabras citando pasos específicos:
* **Dimensión 2:** Architecture, Modularity & Trade-off Soundness.
* **Dimensión 3:** Codebase Conventions & Utility Reuse (Anti-Duplication).
* **Dimensión 4:** Robustness, Safety & API Stability.
* **Dimensión 5:** Instruction Following & Scope Discipline.
* **Dimensión 6:** Planning, Research & Tool Proficiency.
* **Dimensión 7:** Verification & Testing Discipline (Integrity & Hygiene).
* **Dimensión 8:** Intermediate Communication & Risk Explanation.
* **Dimensión 9:** Final Summary & Presentation Quality.
* **Final Quality Score (Side A):** Puntuación global del Lado A.

### Tab D: Agent solution B (Calificación Dimensiones 2-9)
El mismo procedimiento para el Lado B, evaluándolo por sus propios méritos antes de contrastarlo con A.

### Tab E: Rubrics (Creación y Calificación)
* Se deben definir entre 8 y 15 preguntas binarias (donde **SÍ** siempre indica cumplimiento positivo).
* Cada rúbrica se mapea a una dimensión específica.
* Responder SÍ o NO para el Lado A y para el Lado B con citas textuales de pasos o líneas de código.

### Tab F: Pairwise Comparison
* Determinar el modelo ganador o empate.
* **Comparative Rationale obligatorio:** Formato de **3 párrafos** con una longitud estricta de **850 a 1,000 caracteres**. Debe concordar matemáticamente con los puntajes finales asignados en los Tabs C y D.

### Tab G: Deliverable AutoQC
* Ejecuta 17 pruebas automáticas (longitudes mínimas de razones, coherencia de respuestas de rúbricas, límites de caracteres, formato del veredicto comparativo).
* No se puede enviar (`Submit review`) si existe un solo fallo o advertencia activa.

### Tab H: Reviewer Feedback (¡PUNTO CLAVE DE ESTA TAREA!)
Esta tarea fue devuelta previamente por revisores sénior (`Jeremy H` y `Arya A`). Dejaron una **resolución de adjudicación explícita**:

> **Adjudication Rationale de Jeremy H / Arya A:**  
> *"Thanks, solid work here, the dimension reasoning is detailed and your entry citations all check out.*  
> *Two things to fix:*  
> *1. **Rubric 6 side B should be YES.** B did add replacement tests, step 39 adds them and step 61 lists them from test.xml, including `testFileOutput_wrongType`, which covers the case `testDirectoryOutput` used to. As it stands it also contradicts rubric 9's side B reason and your Dimension 7 note about B's six tests.*  
> *2. That flip puts B at 80% pass rate, so you'll need another item or two that both sides genuinely fail. One candidate is that both keep `missing_path` alongside the new wrong-type field, leaving a category the updated test reconstruction no longer handles.*  
> *A few small things I already fixed: Dimension 4 side B said 'two things' but listed one. Rubric 8's side A reason claimed A never reads the field it added, but its `logSymlink` does. Rubric 5's criterion now points at the accessor the repo's tests expect rather than sibling naming."*

---

## 5. ÍNDICE DE ARCHIVOS EXTRAÍDOS Y DISPONIBLES LOCALMENTE

Todo el material extraído de Mercor Studio se encuentra estructurado dentro de esta carpeta:

```
task_74b080f5a1554daaba2595c070f210f7/
├── GUIA_DETALLADA_TAREA.md        # Este documento maestro
├── metadata.json                   # Metadatos del DOM, encabezados e inputs
├── page_raw_text.txt               # Texto íntegro extraído de la plataforma (46k caracteres)
├── page_full.html                  # DOM HTML completo
├── textareas_full.json             # Todos los textareas identificados con índices
├── task_screenshot.png             # Captura visual de la interfaz
├── bundle/                         # Archivos del entorno y solución canónica
│   ├── instruction.md              # Descripción exacta del prompt del usuario
│   ├── task.toml                   # Configuración, categorías, timeout y verifier
│   ├── golden.patch                # Parche de referencia canónico (solución perfecta)
│   ├── Dockerfile                  # Contenedor de ejecución
│   ├── solve.sh                    # Script de resolución
│   ├── grade.py                    # Script evaluador de pruebas
│   ├── test.patch                  # Tests añadidos por SWE-bench
│   ├── test.sh                     # Script de pruebas automáticas
│   └── config.json                 # Configuración de pruebas
├── model_a/                        # Datos del Modelo A
│   ├── final_answer.txt            # Respuesta final del Modelo A
│   ├── logs_summary.txt            # Logs de los 108 pasos
│   └── diff.json                   # Estructura del diff generado por A
├── model_b/                        # Datos del Modelo B
│   ├── final_answer_full.txt       # Respuesta final del Modelo B
│   ├── trajectory_viewer_b.txt     # Trayectoria y pasos 1 a 66
│   └── page_when_model_b_active.txt# Estado visual de la página al activar B
└── tabs/                           # Vistas de contenido de pestañas individuales
    ├── tab_a_how_it_works.txt
    ├── tab_b_task_bundle.txt
    ├── tab_e_rubrics.txt
    ├── tab_g_autoqc.txt
    └── tab_h_feedback.txt
```

---

## 6. HOJA DE RUTA PARA RESOLVER Y APROBAR LA TAREA

Para dejar la tarea en estado perfecto y lista para aprobación final:
1. **Corregir Rúbrica 6 Lado B:** Cambiar a **YES**, citando el paso 39 (donde B introduce `testFileOutput_wrongType`) y el paso 61 (verificación en `test.xml`).
2. **Ajustar la tasa de pase de B (evitar el umbral de 80% artificial):** Incorporar o ajustar una rúbrica donde ambos fallen legítimamente (por ejemplo, mantener `missing_path` simultáneamente con el campo de tipo inválido sin actualizar exhaustivamente la reconstrucción del log).
3. **Verificar que no existan contradicciones internas:** Asegurar que la justificación de Dimensión 7 (Testing) coincida con las respuestas de las Rúbricas 6 y 9.
4. **Validar los conteos de caracteres y palabras:**
   - Cada razón de dimensión: mínimo 15 palabras con citas concretas.
   - Comparative Rationale: exactamente 3 párrafos, entre 850 y 1,000 caracteres.
5. **Ejecutar AutoQC (Tab G):** Verificar que las 17 comprobaciones queden en verde (`Pass`).
