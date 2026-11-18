---
name: compactbench-qc
description: >-
  Pre-validación y reglas operativas para tareas de CompactBench v2 en Mercor Studio.
  Usar antes de hacer Commit de gNN_compaction.md y gNN_compaction_rubric.json para
  pasar Compaction Summary QC y Compaction Rubric QC desde el primer intento.
---

# CompactBench v2 — Guía Operativa y Pre-Validación (AutoQC)

**Objetivo:** Lograr que `COMPACTION SUMMARY QC` y `COMPACTION RUBRIC QC` pasen en verde (`No issues found`) desde el primer `Commit`, protegiendo el **Quality Score (80%)** y cumpliendo las reglas operativas de Slack.

---

## 1. Reglas Operativas Críticas (Slack Announcements & Policy)

1. **Prevención de `Chain Break` y `Admin Flagged`:**
   - **Terminar todas las ediciones de `gNN_compaction.md` ANTES de presionar `Start Compaction`.**
   - **Prohibido** editar un `gNN_compaction.md` intermedio (`g01` cuando ya existe `g02`, etc.) y continuar sin reset. Si editas un golden después de que la siguiente ronda ya inició desde él, el sistema mueve la tarea a **`Chain Break`**.
   - En `Chain Break` aparecen dos opciones en la tarjeta *Golden chain*:
     - `Revert golden`: vuelve al texto anterior del golden y conserva las rondas posteriores.
     - `Rerun from edited golden`: conserva tu edición pero **elimina y re-ejecuta todas las rondas posteriores** (requiere marcar `Confirm rerun`).
   - *Excepción:* Editar **`gNN_compaction_rubric.json` NO dispara `Chain Break`** en ninguna ronda.

2. **Invalidez Cruzada de AutoQCs (*Stale Checks*):**
   - **Cualquier `Commit` en cualquier archivo editable vuelve *stale* (obsoletos) AMBOS checks (`COMPACTION SUMMARY QC` y `COMPACTION RUBRIC QC`).**
   - `Mark Window Complete` exige que **ambos** checks estén vigentes (*current* / `Latest run`) tras el último `Commit` y sin hallazgos bloqueantes abiertos.
   - Si solo necesitas corregir un archivo, edita todo lo necesario primero, haz `Commit` individual por archivo (`No unsaved changes`) y luego corre los checks en secuencia.

3. **Política de Tolerancia Cero en `Dispute`:**
   - Cada disputa es evaluada por **dos modelos** antes de la entrega; si no coinciden, pasa a revisión de un **Admin**.
   - **Regla de pago y permanencia:** Ventanas entregadas con **disputas falsas o checks fallidos NO SE PAGAN**, y tras **2 advertencias** se aplica *offboarding* del proyecto.
   - **Nunca disputar un hallazgo real** (corrígelo en el archivo).
   - Solo si el AutoQC está **objetivamente equivocado**, presenta la disputa con estructura obligatoria:
     `[Código de regla: ej. C2.3 / D1.5] + [Ubicación exacta: view.txt row [N] / línea de gNN_compaction.md / criteria_id] + [Demostración técnica]`. Respuestas vagas como `"This is fine"` se rechazan automáticamente.
   - Si un hallazgo erróneo te bloquea y tienes duda, publícalo en `#compactbench-v2-help-desk` en lugar de forzar la entrega.

4. **Prohibido usar `GNF` (`Golden Needs Fixing`) para Resets:**
   - No enviar tareas a `GNF` para forzar un reset o retener tareas (*hoarding* es motivo de *offboarding*).
   - Si necesitas un reset de ronda (p. ej. fallo del último rollout o `gNN_compaction_rubric.json` vacío `{}` por `VercelGatewayError`), pídelo en el hilo fijado de `#compactbench-v2-announcements` indicando el **URL de Studio** y la **ronda a conservar (`Keep round`)**.

5. **Fallos Silenciosos de AutoQC, Tiempos de Espera e Insightful:**
   - **Fallo silencioso:** A veces AutoQC falla por saturación y devuelve exactamente los mismos hallazgos anteriores con un aviso pequeño de error; verifica que realmente haya corrido (`Latest run`) antes de sobre-editar.
   - **Cuelgues vs. Cola:** Si un check queda estancado en el mismo paso (`1 of 4`, etc.) sin avanzar, cancélalo y relánzalo; ten en cuenta que en horas pico AutoQC puede tardar más de lo habitual.
   - **Insightful e *Idle Reroute*:** El bot de *idle reroute* de Maven reasigna tareas inactivas tras la ventana límite (~2–4 h cuando están de tu lado). Mantén **Insightful** activo únicamente mientras trabajas activamente en la tarea (páusalos durante esperas pasivas sin tareas).

---

## 2. Reglas Técnicas del Golden Summary (`gNN_compaction.md`)

* **C3.3 — 1 hecho = 1 bullet (atomicidad estricta en TODAS las secciones, incluyendo `Work State`, `Next Move` y `Relevant Files`):**
  * **Archivos leídos (`Work State -> Completed`):** Nunca listar varios archivos en un solo bullet (`Read a.py, b.py, c.py` → separar en 1 bullet por archivo o fuente única).
  * **Diseños definidos (`Work State -> Completed`):** Nunca juntar varios artefactos (`Settled design for A, B, and C` → 1 bullet por artefacto).
  * **Pasos pendientes (`Next Move`):** Nunca juntar dos cambios o dos verificaciones en un paso (`wire X while removing Y`, `add target and add deps`, `verify dlc keys and signal preservation`, `skip signals and print names` → pasos separados).
  * **Hipótesis + Directiva:** Nunca unir una creencia/hallazgo con una instrucción (`...may hit KeyError; avoid black_list in tests` → 2 bullets).
* **C2.1 — Solo `view.txt`, prohibido `tail.txt`:**
  * El compactador no vio `tail.txt`. Todo plan o verificación en `gNN_compaction.md` debe provenir de `view.txt` (ej. no meter procedimientos que solo aparecen en `tail.txt`).
* **C2.2 — Incertidumbres resueltas en `tail.txt`:**
  * Si algo era incierto en `view.txt` pero se resuelve en `tail.txt`, calificarlo explícitamente como *"remains unverified at view time"*.
* **C2.3 / D2.6 — Archivos `[truncated]` en `view.txt`:**
  * Si la salida de un archivo en `view.txt` se cortó con `[truncated]` antes de la definición citada, **nunca** escribir *"semantics were confirmed"*; escribir *"the agent inferred/noted ... (truncated in view; unverified)"*.
* **G24 — Firmas y defaults decididos:**
  * Incluir explícitamente en `Important Details` las firmas de constructores/funciones y valores por defecto decididos en `view.txt` (ej. `UnsupportedSignalError.__init__(signal_name, message=None)` y `SignalLayout.__init__(slices=(), bit_width=0)`).
* **D1.7 — Sin números de línea frágiles:** No usar referencias posicionales como `at line 450`.

---

## 3. Reglas Técnicas de la Rúbrica (`gNN_compaction_rubric.json`)

* **D1.4 — Proporción de `major`:** Entre **25% y 40%** de los criterios positivos (apuntar a **28%–33%**).
* **D1.5 — Tope de longitud (`Compression efficiency`):** Exactamente `Contains at most <CAP> characters.` donde `<CAP> = ceil_100(1.1 * len(gNN_compaction.md))`. Recalcular siempre tras cualquier cambio en `gNN_compaction.md`.
* **D1.6 — `Structural clarity`:** Prohibido calificar layout, párrafos, listas o agrupación visual. Debe evaluar un hecho técnico atómico soportado por `view.txt`.
* **D2.4 — `task-echo` <= 25% y sin historia irrelevante:**
  * El peso positivo (`major=2, minor=1`) de los criterios que pueden responderse solo con el prompt inicial (`instruction.md`) debe ser **< 25%** del peso positivo total. Priorizar hechos descubiertos y decisiones tomadas durante la corrida.
  * No premiar repeticiones históricas o inventarios triviales de directorios (`codex-path contained only rg`).
* **D2.5 — Peso de *Next Steps*:** Los pasos siguientes críticos pendientes no deben sub-ponderarse como `minor` cuando representan una acción/decisión clave pendiente (`major`).
* **D2.1 / D2.2 / D2.3 — Forma de los criterios (`Criterion shape part 1..4`):**
  * *Nota de partición:* El evaluador divide los criterios por `index % 4` (`idx % 4 == 1 -> part 1`, `2 -> part 2`, `3 -> part 3`, `0 -> part 4`).
  * **D2.1 (Atómico):** 1 solo método, campo o cambio por criterio (no unir `get_byte and set_value`, ni `byte 8 and skipped`, ni `add dlc and drop filter`).
  * **D2.2 (Literal y sin ambigüedad aritmética):** Usar paréntesis explícitos en fórmulas en prosa o código (`lengthDot * (terminationTension - originTension)`).
  * **D2.3 (Auto-contenido y trazable a `view.txt`):** Nombrar explícitamente las funciones/archivos evaluados (no decir *"the scalar queries"* o *"existing helpers"*), no exigir umbrales numéricos que no estén en `view.txt`, y no evaluar justificaciones de diseño que el agente no haya expresado en `view.txt`.
* **D1.7 — Prohibido en criterios:** Números de línea (`at line N`) y fallos transitorios de invocación de herramientas (`apply_patch: command not found`).
* **D1.9 / D2.7 / D2.8 / D2.11 — `Penalties and pairs`:**
  * **Cero doble puntaje:** Ninguna oración válida debe poder satisfacer 2 criterios positivos a la vez (no duplicar el mismo hecho entre *Goal fidelity*, *Artifact preservation* y *Temporal coherence*, ni separar en dos criterios dos elementos que `view.txt` enuncia en una misma frase corta).
  * **3 criterios `negative` al final:** Deben ser afirmaciones claramente falsas según `view.txt`, que **no** coincidan con ninguna afirmación verdadera del golden y que no contradigan de forma confusa el texto literal de un criterio positivo en su misma partición `idx % 4`.

---

## 4. Script de Pre-Validación Automática

Ejecutar siempre antes de inyectar y hacer `Commit` en Mercor Studio:
```powershell
python .agents/skills/compactbench-qc/scripts/precheck.py <task_dir> <window> <point>
# Ejemplo:
python .agents/skills/compactbench-qc/scripts/precheck.py task_5b6365b8b1de4492a09edaf3a1aad92a 128K g01
```
