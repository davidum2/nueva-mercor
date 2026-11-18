---
name: compactbench-qc
description: >-
  Suite de auditoría forense, pre-validación automática (Zero-Blocker Gate) y commit seguro
  para tareas de CompactBench v2 en Mercor Studio. Usar en cada tarea nueva antes de editar
  y antes de hacer Commit de gNN_compaction.md y gNN_compaction_rubric.json para pasar
  Compaction Summary QC y Compaction Rubric QC desde el primer intento.
---

# CompactBench v2 — Suite de Auditoría y Pre-Validación (`v2.0`)

**Objetivo:** Pasar `COMPACTION SUMMARY QC` (4/4) y `COMPACTION RUBRIC QC` (10/10) en **`No issues found` desde el primer `Commit`**, protegiendo el **Quality Score (80%)** y cumpliendo las reglas de Slack sin regresiones.

---

## 1. Pipeline Obligatorio en 4 Pasos

```powershell
# Paso 1: Extraer TODOS los archivos (incluyendo SIEMPRE view.txt y tail.txt)
python .agents/skills/compactbench-qc/scripts/extract_task.py <task_id> <window> <point>

# Paso 2: Auditoria forense de view.txt, tail.txt y gNN_state.patch (ANTES de editar)
python .agents/skills/compactbench-qc/scripts/audit_view.py <task_id> <window> <point>

# Paso 3: Pre-validacion integral (Zero-Blocker Gate) tras editar golden y rubric
python .agents/skills/compactbench-qc/scripts/precheck.py <task_id> <window> <point>

# Paso 4: Commit seguro en Mercor Studio (ejecuta precheck.py primero; aborta si hay BLOCKERS)
python .agents/skills/compactbench-qc/scripts/commit_task.py <task_id> <window> <point>
```

---

## 2. Reglas Operativas Críticas (Slack Policy)

1. **`Chain Break` y `Admin Flagged`:**
   - Terminar **todas** las ediciones de `gNN_compaction.md` **antes** de `Start Compaction`.
   - **Prohibido** editar un `gNN_compaction.md` intermedio (`g01` cuando ya existe `g02+`) sin reset o `Rerun from edited golden`.
   - Editar `gNN_compaction_rubric.json` **no** dispara `Chain Break`.
2. **Invalidez Cruzada (*Stale QCs*):**
   - Cualquier `Commit` en cualquier archivo editable vuelve *stale* **ambos** checks (`Summary QC` y `Rubric QC`).
   - `Mark Window Complete` exige ambos checks vigentes (`Latest run`) y en verde tras el último `Commit`.
   - Regla de `run_stats.json`: Si `"winner_passed": true` ya existe y solo corriges formato/atomicidad o rúbrica, **no** presiones `Start Compaction`.
3. **Tolerancia Cero en `Dispute`:**
   - Dos modelos + Admin validan cada disputa. Disputas falsas o entregas con checks fallidos = **no pago** y *offboarding* tras 2 advertencias.
   - Nunca disputar hallazgos reales; solo disputar errores objetivos del QC con formato `[Regla] + [view.txt row N / línea / criteria_id] + [Demostración]`.
4. **Prohibido enviar a `GNF`:** Pedir resets (o regeneración de rúbrica vacía `{}` por `VercelGatewayError`) en el hilo oficial de `#compactbench-v2-announcements` con URL y `Keep round`.
5. **Fallos silenciosos e Insightful:** Verificar que el check corrió (`Latest run`) antes de re-editar; mantener Insightful activo solo en trabajo activo y vigilar *idle reroute* (~2–4 h).

---

## 3. Reglas Duras del Golden Summary (`gNN_compaction.md`)

### A. `Golden form (C3.1–C3.4)`
* **C3.1/C3.2 — Cero meta-referencias al proceso:** Nunca escribir dentro del golden palabras como `view`, `in view`, `view time`, `compactor`, `compaction`, `handoff`, `summary`, `context window`, `kept tail`, `tail.txt`, `view.txt`.
* **C3.3 — 1 hecho = 1 bullet en TODAS las secciones (`Objective`, `Important Details`, `Work State`, `Next Move`, `Relevant Files`):**
  * **Prohibido cuantificadores agregados:** nunca escribir *"Each of the three stages..."*, *"Both callbacks..."*, *"These queries..."*, *"Origin and termination forces..."* → escribir 1 bullet por archivo/método/ubicación.
  * **Prohibido listas en `Work State -> Completed`:** 1 bullet por archivo leído y 1 bullet por artefacto con diseño definido.
  * **Prohibido verbos/acciones dobles en `Next Move`:** nunca `wire X and skip printing`, `wire X while removing Y`, `add target and deps`, `omitted and printed`, `verify A and B`, `sanity-test A, B, and C`.
  * **Prohibido casos opuestos o defaults múltiples en 1 bullet:** separar `convex` vs `concave`, `positive rate` vs `negative rate`, `not in contact` vs `in contact`, y cada tipo de default (`bool`, `int`, `double`, `enum`).
  * **Prohibido `A and B` en `Relevant Files`:** 1 bullet por método o componente (`Byte::get_byte` y `Byte::set_value` separados; codec model y helper separados).
  * **Prohibido mezclar estado/hecho + directiva/plan:** separar `hypothesis` de `plan`, `file behavior` de `leave untouched`, `compile failed` de `tests not run`, `slicing` de `encode write order`.

### B. `Golden evidence (C1.1, C1.2, C1.3, C4.1)`
* **C1.1/C1.2 — Prohibido sobre-generalizar lecturas:** Nunca escribir *"Read the files/templates/code under dir/"*. Listar únicamente los archivos exactos leídos en `view.txt`, y distinguir explícitamente `Read` de `Grepped`.
* **C1.2/C4.1 — Cero filtración de `tail.txt` ni consejos inventados:** No inventar consejos de pruebas ni copiar planes exclusivos de `tail.txt` (`extract_dbc_meta`, `synthetic DBC`, `different DBC`) que no estén en `view.txt`.
* **C1.3 — Archivos `[truncated]` y código no mostrado en tool outputs:**
  * Usar `audit_view.py` para ver qué archivos se cortaron con `[truncated]` en `view.txt`.
  * Todo comportamiento de código que aparezca solo en *reasoning* (después del truncado o en C++ generado no mostrado) **debe atribuirse al agente** (*"Based on the agent's finding (file read truncated before ...)"*, *"the agent reasoned..."*), nunca como `"confirmed"`.

### C. `Golden state and decisions (C2.1–C2.6, G24)`
* **G24 / C2.6 — Decisiones asentadas obligatorias:** Incluir explícitamente todas las firmas, defaults de constructores y decisiones de estilo asentadas (ej. `UnsupportedSignalError.__init__(signal_name, message=None)`, `SignalLayout.__init__(slices=(), bit_width=0)`, omisión de anotaciones de tipo en runtime).
* **C2.1 — Coherencia con estado y factibilidad:** No planear verificaciones imposibles según `view.txt` (ej. probar >32 bits en un DBC cuyo máximo es 16 bits), ni afirmar como editado algo cuando `gNN_state.patch` tiene 0 bytes.

---

## 4. Reglas Duras de la Rúbrica (`gNN_compaction_rubric.json`)

* **D1.4 — Ratio `major`:** Estrictamente **25%–40%** de los criterios positivos (zona segura: **28%–35%**).
* **D1.5 — `Compression efficiency`:** Exactamente `Contains at most <CAP> characters.` donde `<CAP> = ceil_100(1.1 * len(gNN_compaction.md))`. Colocarlo preferentemente en índice `idx % 4 == 0` (`Part 4`) para evitar falsos positivos en `Part 3`.
* **D1.6 — `Structural clarity`:** Nunca evaluar layout, párrafos, listas ni agrupación. Usar un hecho atómico verificable de `view.txt`.
* **D1.7 — Prohibidos absolutos:** Cero números de línea (`at line 450`) y cero fallos transitorios de herramienta (`apply_patch: command not found`, `did not execute`).
* **D2.1 — Atomicidad y prohibición de plurales:** 1 solo archivo, método, campo o cambio por criterio. Evitar plurales (`stage imports`, `emission stages`, `public methods`, `scalar queries`).
* **D2.2 — Sin ambigüedad aritmética ni léxica:** Usar paréntesis explícitos en fórmulas (`lengthDot * (terminationTension - originTension)`) y acciones inequívocas.
* **D2.3 — Auto-contención estricta:** Nombrar explícitamente `archivo::función` (nunca `"the existing emitter"`, `"the chosen helper"`, `"existing helpers"`). No exigir umbrales numéricos ni justificaciones que no estén literalmente en `view.txt`.
* **D2.4 — `task-echo < 25%` y sin historia/trivia:** El peso positivo (`major=2, minor=1`) de criterios respondibles solo desde `instruction.md` debe ser **< 25%**. Eliminar repeticiones históricas e inventarios triviales.
* **D2.5 — Pesos `major` obligatorios:** Todos los *success criteria* explícitos (ej. *"accepted signals must remain unchanged"*) y todos los *next steps* clave pendientes deben ser **`major`**.
* **D2.6 / Criterion truth:** Si `gNN_state.patch` está vacío (0 bytes), ningún criterio positivo puede usar verbos de cambio ya ejecutado (`is removed`, `was added`); usar `"is planned to be..."`. Si un archivo estuvo `[truncated]` en `view.txt`, calificar el criterio como *inferred by the agent (unverified)*.
* **D1.9 / D2.7 / D2.8 / D2.11 — Cero doble puntaje y 3 `negative`:**
  * Revisar cualquier par de criterios positivos que compartan archivo/símbolo entre categorías (*Goal fidelity* ↔ *Artifact preservation* ↔ *Temporal coherence*) para que una misma frase nunca sume 2 puntos.
  * Incluir 3 criterios `negative` al final que contradigan claramente hechos de `view.txt`, no aparezcan en el golden, y no choquen en la misma partición `idx % 4` con un criterio positivo.
