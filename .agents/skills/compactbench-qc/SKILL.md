---
name: compactbench-qc
description: >-
  Suite de auditoría forense, pre-validación automática (Zero-Blocker Gate) y commit seguro
  para tareas de CompactBench v2 en Mercor Studio. Usar en cada tarea nueva antes de editar
  y antes de hacer Commit de gNN_compaction.md y gNN_compaction_rubric.json para pasar
  Compaction Summary QC y Compaction Rubric QC desde el primer intento.
---

# CompactBench v2 — Suite de Auditoría y Pre-Validación (`v2.8`)

**Objetivo:** Pasar `COMPACTION SUMMARY QC` (4/4) y `COMPACTION RUBRIC QC` (10/10) en **`No issues found` desde el primer `Commit`**, protegiendo el **Quality Score (80%)** y cumpliendo las reglas de Slack sin regresiones.

---

## 1. Pipeline Obligatorio en 4 Pasos

```powershell
# Paso 1: Extraer TODOS los archivos (incluyendo SIEMPRE view.txt y tail.txt)
python .agents/skills/compactbench-qc/scripts/extract_task.py <task_id> <window> <point>

# Paso 2: Auditoria forense de view.txt, tail.txt y gNN_state.patch (ANTES de editar)
# Genera <task_dir>/_audit_decisions.txt con TODAS las decisiones G24/C2.6 completas (sin corte a 20 lineas ni a 180 chars)
python .agents/skills/compactbench-qc/scripts/audit_view.py <task_id> <window> <point>

# Paso 3: Pre-validacion integral (Zero-Blocker Gate v2.3) tras editar golden y rubric
python .agents/skills/compactbench-qc/scripts/precheck.py <task_id> <window> <point>

# Paso 4: Commit seguro en Mercor Studio (soporta --only rubric o --only golden para no re-commitear archivos ya en verde)
python .agents/skills/compactbench-qc/scripts/commit_task.py <task_id> <window> <point> [--only rubric|golden]
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
5. **Fallos silenciosos, historial `Run X of Y` e Insightful (`v2.3`):** Verificar **siempre** que ambos paneles muestren **`Latest run`** (nunca `Run 4 of 5` mientras `Run 5 (Latest)` tenga fallos ocultos en el dropdown!). Si aparece el pop-up *"AutoQC already scored this unchanged task"*, abrir el selector de historial y revisar el run `Latest`. Mantener Insightful activo solo en trabajo activo y vigilar *idle reroute* (~2–4 h).

---

## 3. Reglas Duras del Golden Summary (`gNN_compaction.md`)

### A. `Golden form (C3.1–C3.4)`
* **C3.1/C3.2 — Cero meta-referencias al proceso:** Nunca escribir dentro del golden palabras como `view`, `in view`, `view time`, `compactor`, `compaction`, `handoff`, `summary`, `context window`, `kept tail`, `tail.txt`, `view.txt`.
* **C3.4 — Encabezados exactos del harness (`v2.9`):** Conservar **exactamente** los encabezados del baseline/plantilla del harness (p. ej. en OpenCode: `## Objective`, `## Important Details`, `## Work State` con `### Completed`/`### Active`/`### Blocked`, `## Next Move`, `## Relevant Files`) **sin agregar `###` extra** debajo de `## Important Details`.
* **C3.3 — 1 hecho = 1 bullet en TODAS las secciones (`Objective`, `Important Details`, `Work State`, `Next Move`, `Relevant Files`):**
  * **Prohibido cuantificadores agregados:** nunca escribir *"Each of the three stages..."*, *"Both callbacks..."*, *"These queries..."*, *"Origin and termination forces..."* → escribir 1 bullet por archivo/método/ubicación.
  * **Prohibido listas en `Work State -> Completed`:** 1 bullet por archivo leído y 1 bullet por artefacto con diseño definido.
  * **Prohibido verbos/acciones dobles en `Next Move`:** nunca `wire X and skip printing`, `wire X while removing Y`, `add target and deps`, `omitted and printed`, `verify A and B`, `sanity-test A, B, and C`.
  * **Prohibido casos opuestos o defaults múltiples en 1 bullet:** separar `convex` vs `concave`, `positive rate` vs `negative rate`, `not in contact` vs `in contact`, y cada tipo de default (`bool`, `int`, `double`, `enum`).
  * **Prohibido `A and B` en `Relevant Files`:** 1 bullet por método o componente (`Byte::get_byte` y `Byte::set_value` separados; codec model y helper separados).
  * **Prohibido cláusulas participiales, resultados dobles o `retorno + excepción` (`v2.1`):** nunca escribir `..., leaving/returning/raising ...`, `calls/returns X and raises Y`, ni `yields X and will be skipped and reported` → separar cada comportamiento/resultado en un bullet independiente.
  * **Prohibido verbos/acciones dobles en tercera persona o secuenciales (`v2.6` BLOCKER):** nunca escribir `and sets/calls/disables/enables/accepts/forwards/clears/forces`, `followed by`, ni `, then calls/sets/clears` → separar en 2 bullets atómicos.
  * **Disciplina Zero-Warning en `C3.3`:** además de eliminar todos los `[BLOCKER]`, revisar y limpiar los `[WARN]` de `precheck.py` (listas de 3+ símbolos, `;` fuera de backticks, pares `A` and `B` de hechos independientes) para evitar el *efecto cebolla* donde el LLM juez destapa nuevos bullets compuestos en la siguiente corrida.

### B. `Golden evidence (C1.1, C1.2, C1.3, C4.1)`
* **C1.1/C1.2 — Identificadores y variables exactas de `view.txt` (`v2.7` BLOCKER):** Todo símbolo de código entre backticks (con `_`, `CamelCase`, `Class.method` o `var[idx]`) tanto en el golden como en la rúbrica **debe existir literalmente en `view.txt`** (ej. nunca usar `gslc_Init` si solo aparece en `tail.txt`, ni `FrameCodec.quantize` si `view.txt` solo usa `quantize`). Verificado automáticamente en `precheck.py`.
* **C1.1/C1.2 — Prohibido sobre-generalizar lecturas:** Nunca escribir *"Read the files/templates/code under dir/"*. Listar únicamente los archivos exactos leídos en `view.txt`, y distinguir explícitamente `Read` de `Grepped`.
* **C1.2/C2.3/C4.2 — Cero filtración de `tail.txt` ni consejos inventados:** No inventar consejos de pruebas ni copiar hechos o decisiones exclusivos de `tail.txt` (ej. anotaciones de tipo Python pre-3.10 o procedencia real de un DBC descubierta tras el corte) **aunque un AutoQC previo los mencione por error**. Cada hecho del golden debe existir en `view.txt`.
* **C1.3 — Archivos `[truncated]` y código no mostrado en tool outputs:**
  * Usar `audit_view.py` para ver qué archivos se cortaron con `[truncated]` en `view.txt`.
  * Todo comportamiento de código que aparezca solo en *reasoning* (después del truncado o en C++ generado no mostrado) **debe atribuirse al agente** (*"Based on the agent's finding (file read truncated before ...)"*, *"the agent reasoned..."*), nunca como `"confirmed"`.

### C. `Golden state and decisions (C2.1–C2.6, G24)`
* **G24 / C2.6 — Decisiones asentadas Y SU MOTIVO obligatorios (`v2.2`):** Revisar el archivo completo `<task_dir>/_audit_decisions.txt` (líneas íntegras sin corte a 180 chars) e incluir explícitamente todas las firmas, defaults, políticas de nombres/case-sensitivity, rutas scratch y decisiones de no modificar algo (`chose to leave ... unchanged`, `planned to leave ... untouched`). **Nunca dejar una decisión desnuda sin su motivo (`because / pre-existing / outside scope`)**, porque `C2.6` bloquea si se omite el *rationale*.
* **C2.1 / C2.2 — Coherencia con estado y con `tail.txt` (`v2.2`):**
  * No planear verificaciones imposibles según `view.txt` ni afirmar como editado algo cuando `gNN_state.patch` tiene 0 bytes.
  * **Regla de Oro `C2.2` vs `Golden evidence`:** Si una suposición temprana de `view.txt` es refutada después en `tail.txt`, **NO** copiar el hallazgo de `tail.txt` (rompe `Golden evidence`), pero **tampoco** preservar la suposición refutada (dispara `C2.2`); **omitir la especulación superada** y conservar solo hechos neutros observables en `view.txt`.

---

## 4. Reglas Duras de la Rúbrica (`gNN_compaction_rubric.json`)

* **D1.4 — Ratio `major`:** Estrictamente **25%–40%** de los criterios positivos (zona segura: **28%–35%**).
* **D1.5 — `Compression efficiency` (`v2.4` BLOCKER):** Exactamente `Contains at most <CAP> characters.` donde `<CAP> = ceil_100(1.1 * len(gNN_compaction.md))`. **Prohibido** dejarlo en índice `idx % 4 == 3` (`Part 3`); colocarlo siempre en `idx % 4 == 0` (`Part 4`) para evitar el falso positivo `D2.3` de `Part 3`.
* **D2.8 — Duplicados Jaccard >= 0.70 (`v2.4` BLOCKER):** Nunca incluir dos criterios casi idénticos que puedan premiar la misma frase (ej. `Byte::get_byte` y `Byte::set_value` con misma calificación de truncado) — conservar solo uno para evitar `Penalties and pairs` sin romper `D2.1`.
* **D1.6 — `Structural clarity` (`v2.8` P26):** Debe existir **exactamente 1** criterio `Structural clarity` (`minor`) **harness-neutral sobre la organización del resumen** (ej. *"Keeps the outstanding implementation steps together so pending work is directly findable."*), **sin** nombrar headings, secciones, orden, párrafos, bullets ni formato de lista. Nunca sustituirlo por un hecho técnico de código ni por nombres de secciones.
* **D1.9 — Negativos sin doble puntaje (`v2.8`):** Ningún criterio `negative` puede ser el inverso directo de un criterio positivo existente (ej. si hay un positivo `"no code changes have been made"`, prohibido poner un negativo `"changes have already been applied"`). Penalizar fabricaciones graves sobre requisitos/hechos **no** puntuados directamente por otro positivo (ej. `malloc` prohibido, override prohibido).
* **D1.7 — Prohibidos absolutos:** Cero números de línea (`at line 450`) y cero fallos transitorios de herramienta (`apply_patch: command not found`, `did not execute`).
* **D2.1 — Atomicidad y prohibición de plurales:** 1 solo archivo, método, campo o cambio por criterio. Evitar plurales (`stage imports`, `emission stages`, `public methods`, `scalar queries`).
* **D2.2 — Sin ambigüedad aritmética ni léxica:** Usar paréntesis explícitos en fórmulas (`lengthDot * (terminationTension - originTension)`) y acciones inequívocas.
* **D2.3 — Auto-contención estricta:** Nombrar explícitamente `archivo::función` (nunca `"the existing emitter"`, `"the chosen helper"`, `"existing helpers"`). No exigir umbrales numéricos ni justificaciones que no estén literalmente en `view.txt`.
* **D2.4 — `task-echo < 25%` y sin historia/trivia (`v2.6` BLOCKER):** El peso positivo (`major=2, minor=1`) de criterios respondibles solo desde `instruction.md` debe ser **< 25%**. Eliminar repeticiones históricas, inventarios triviales y criterios de historial git (`branch master at commit ...`, `git log`, `head commit`).
* **D2.5 — Pesos `major` obligatorios:** Todos los *success criteria* explícitos (ej. *"accepted signals must remain unchanged"*) y todos los *next steps* clave pendientes deben ser **`major`**.
* **D2.6 / Criterion truth (`v2.3`):** Si `gNN_state.patch` está vacío (0 bytes), ningún criterio positivo puede usar verbos de cambio completado **ni presente activo** (`is removed`, `was added`, `as setting`, `removes the`, `as adding`); usar siempre `"Records the planned addition/removal..."` o `"plans to..."`. Todo comportamiento de archivo `[truncated]` en `view.txt` o código generado no mostrado debe calificarse explícitamente como `agent's finding`, `agent's reasoned design decision` o `agent's unverified inference`.
* **D2.1 en Rúbrica (`v2.3`):** Cero pares `` `A` and `B` `` de propiedades/campos independientes dentro de un criterio (bloqueado en `precheck.py`) y cero frases vagas como `"round-trips against the generated C++ logic"` (`D2.2`).
* **D1.9 / D2.7 / D2.8 / D2.11 — Cero doble puntaje y 3 `negative`:**
  * Revisar cualquier par de criterios positivos que compartan archivo/símbolo entre categorías (*Goal fidelity* ↔ *Artifact preservation* ↔ *Temporal coherence*) para que una misma frase nunca sume 2 puntos.
  * Incluir 3 criterios `negative` al final que contradigan claramente hechos de `view.txt`, no aparezcan en el golden, y no choquen en la misma partición `idx % 4` con un criterio positivo.
