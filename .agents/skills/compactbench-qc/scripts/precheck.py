"""
Pre-validacion integral v2.8 para CompactBench v2 (Golden + Rubric + State + View + Tail + Slack Rules).
Actua como Zero-Blocker Gate ANTES de cualquier Commit en Mercor Studio.

Uso:
  python .agents/skills/compactbench-qc/scripts/precheck.py <task_dir> <window> <point> [--strict]
"""
import json
import math
import os
import re
import sys


REQUIRED_CATEGORIES = {
    "Goal fidelity",
    "Artifact preservation",
    "Decision rationale",
    "Temporal coherence",
    "Structural clarity",
    "Compression efficiency",
}

# Meta-palabras prohibidas en gNN_compaction.md (Golden form C3.1/C3.2)
GOLDEN_META_PATTERN = re.compile(
    r"\b(view time|in view|in the view|from the view|compactor|compaction|handoff|context window|kept tail|tail\.txt|view\.txt)\b",
    re.I,
)

# Patrones de bullets compuestos en gNN_compaction.md (C3.3)
GOLDEN_COMPOUND_PATTERNS = [
    (r"^-\s+Read\s+.*,.*", "C3.3: bullet 'Read ...' lista multiples archivos (1 archivo por bullet)"),
    (r"^-\s+Read\s+the\s+.*(?:files|code|templates)\s+under\b", "C1.1/C1.2: sobre-generaliza lecturas por carpeta (listar solo archivos leidos)"),
    (r"^-\s+Settled the design for\s+.*,.*", "C3.3: 'Settled the design...' une multiples artefactos (1 por bullet)"),
    (r"\bboth\s+(?:the\s+)?(?:`[^`]+`|[\w./-]+)(?:\s+[\w./-]+)?\s+and\s+(?:the\s+)?(?:`[^`]+`|[\w./-]+)", "C3.3: 'both X and Y' une dos entidades/ramas independientes en un bullet (separar en 2 bullets)"),
    (r"\b(?:each of the (?:two|three|four|five|\d+)|all (?:two|three|four|five|\d+)\s+\w+|each (?:emission )?stage|every (?:emission )?stage|the (?:two|three|four) (?:emission )?stages)\b", "C3.3: cuantificador agregado ('Each/All/Every/the three stages') une multiples entidades independientes"),
    (r"\bneither\s+[^,.;:]+\bnor\b", "C3.3: 'neither X nor Y' une dos afirmaciones independientes"),
    (r"\bwhile\s+(?:removing|adding|updating|keeping|printing|skipping|preserving|leaving)\b", "C3.3: une dos acciones con 'while <verbo>-ing' (separar en 2 bullets)"),
    (r"\btarget and deps\b|\btarget and .* dependencies\b", "C3.3: une creacion de target BUILD con dependencias (separar)"),
    (r"\bto verify\b.*\band\b", "C3.3: une dos verificaciones distintas en un solo paso ('to verify A and B')"),
    (r"\bskip\b.*\band print\b|\band skip printing\b", "C3.3: une 'skip/wire' con 'print' en un mismo bullet"),
    (r"\band\s+(?:printed|omitted|reported|skipped|dropped|added|removed|updated|wired|checked|verified|scaled|reset|planned|raised|returned|truncated|clamped)\b", "C3.3: une dos comportamientos/resultados con 'and <participio>'"),
    (r"\band\s+(?:print|omit|report|skip|drop|add|remove|update|wire|check|verify|diff|test|run|raise|return)\b", "C3.3: une dos acciones imperativas con 'and <verbo>'"),
    (r"\band\s+(?:sets|calls|disables|enables|accepts|forwards|clears|forces|restores|delegates|reads)\b", "C3.3: une dos acciones en tercera persona con 'and <verbo>s' (separar en 2 bullets)"),
    (r"\bfollowed by\b|,\s+then\s+(?:calls|sets|clears|runs|restores|resets|updates|returns)\b", "C3.3: une dos pasos secuenciales con 'followed by' o ', then <verbo>' (separar en 2 bullets)"),
    (r",\s+(?:leaving|returning|raising|skipping|printing|reporting|keeping|writing|truncating|preserving)\b", "C3.3: clausula participial tras coma (', leaving/returning/raising...') agrega un segundo comportamiento"),
    (r"\byields\b.*\band will be\b|\breturns\b.*\band raises\b|\bcalls\b.*\band raises\b", "C3.3: une dos resultados o retorno + excepcion en un solo bullet"),
    (r"\bdefault(?:s)? to\b.*,.*,.*and\b", "C3.3: lista multiples valores por defecto por tipo en un solo bullet (separar 1 por tipo)"),
    (r"\bwhen not in contact and otherwise\b|\bfor positive .* and .* for negative\b|\bpositive on .* and negative on\b", "C3.3: une dos casos opuestos (positivo/negativo, contacto/sin contacto) en un bullet"),
]

# Decisiones sin justificacion en gNN_compaction.md (C2.6)
BARE_DECISION_PATTERN = re.compile(
    r"\b(?:chose to|decided to|opted to|planned to leave|will leave|remains? untouched|remain untouched|left .* unchanged|leave .* unchanged|leave .* untouched)\b",
    re.I,
)
RATIONALE_MARKER_PATTERN = re.compile(
    r"\b(?:because|since|due to|so that|mirroring|matching|rather than|outside|out of scope|pre-existing|to avoid|to match|to preserve|given that|limited to)\b",
    re.I,
)

# Frases prohibidas en criterios de rubrica (D1.6, D1.7, D2.2)
FORBIDDEN_RUBRIC_PHRASES = [
    (r"\bat line \d+\b|\bline \d+\b", "D1.7: prohibido citar numeros de linea en criterios"),
    (r"\bparagraphs?\b|\blist items?\b|\bbullet(?:s)?\b|\bheadings?\b|\bseparate sections?\b|\bsection(?:s)?\b|\bpresents\b.*\bseparately from\b|\bwithout reading the whole\b", "D1.6/D2.2: prohibido nombrar headings, secciones, orden, parrafos o formato de lista en criterios"),
    (r"\bcommand not found\b|\bdid not execute\b|\bfailed patch\b|\bone-off\b|\btruncated early\b|\btruncation\b", "D1.7: prohibido incluir errores/truncados transitorios de herramientas"),
    (r"\bsuch as\b", "D2.2: evitar 'such as' en criterios (especificar el simbolo/conjunto exacto verificable)"),
    (r"\bat commit `?[\da-f]{7,40}`?\b|\bgit log\b|\bhead commit\b", "D2.4: trivia de historial git (branch/commit hash) no necesaria para continuacion"),
]

# Referentes vagos sin nombre en criterios de rubrica (D2.3)
VAGUE_RUBRIC_REFERENTS = [
    (r"\bthe existing emitter\b|\bthe emitter(?:'s)?\b", "D2.3: nombrar archivo::funcion en lugar de 'the emitter'"),
    (r"\bthe chosen\b", "D2.3: nombrar el helper/metodo exacto en lugar de 'the chosen ...'"),
    (r"\bthe required patch tool\b", "D2.3: nombrar la herramienta exacta (ej. apply_patch)"),
    (r"\bexisting unit-force helpers\b|\bexisting helpers\b", "D2.3: nombrar cada helper exacto"),
    (r"\bthe scalar (?:tension|power|queries)\b|\bnew (?:tension|power|force) apis\b", "D2.3: nombrar los metodos publicos exactos"),
    (r"\bstage imports\b|\bemission stages\b|\bthree stage targets\b|\bthree emission stages\b", "D2.1: plural agrupa multiples archivos/stages en un solo criterio"),
]

# Verbos de hecho completado o presente activo prohibidos cuando gNN_state.patch esta vacio (D2.6 / Criterion truth)
COMPLETED_EDIT_VERBS = re.compile(
    r"\b(?:is removed|was removed|were removed|is added|was added|were added|has been added|have been added|"
    r"is modified|was modified|were modified|has been written|have been written|"
    r"as setting|as adding|as removing|removes the|adds an|adds a|adds the|sets the|drops the|modifies the)\b",
    re.I,
)
PLANNED_EDIT_QUALIFIERS = re.compile(
    r"\b(?:planned|pending|plan to|plans to|must|requirement|no files|will be|to be)\b",
    re.I,
)
TRUNC_TRUTH_QUALIFIERS = re.compile(
    r"\b(?:inferred|inference|reasoned|reasoning|rejected|agent's finding|agent finding|unverified|planned|plan|plans|pending|must|requirement|truncated|hypothesis|re-plumb|has not (?:yet )?been read|remains unread|unread)\b",
    re.I,
)

# Patrones de ambiguedad aritmetica o lexica (D2.2)
AMBIGUOUS_MATH_PATTERNS = [
    (r"\b(?:multiplied by|times)\s+[^()`]+\b(?:minus|plus)\b", "D2.2: posible ambiguedad aritmetica sin parentesis (usar expresion parentizada en backticks)"),
    (r"\btarget dependencies\b", "D2.2: frase ambigua ('target dependencies' vs target + deps)"),
]


def find_truncated_files_in_view(view_path: str):
    if not os.path.exists(view_path):
        return set()
    with open(view_path, encoding="utf-8", errors="ignore") as f:
        content = f.read()
    truncated_files = set()
    for m in re.finditer(r"([A-Za-z0-9_./-]+\.(?:py|cc|cpp|c|h|hpp|proto|dbc|sh|json|toml|md|tpl|bzl))", content):
        start = m.start()
        window = content[start:start + 2500]
        if "[truncated]" in window or "more characters truncated" in window or "chars truncated" in window:
            bn = os.path.basename(m.group(1))
            if bn and len(bn) > 3 and not bn.startswith("."):
                truncated_files.add(bn)
    return truncated_files


def check_chain_break_risk(task_dir: str, window: str, point: str):
    blockers = []
    win_dir = os.path.join(task_dir, "golden", window)
    if not os.path.isdir(win_dir):
        return blockers
    points = sorted([d for d in os.listdir(win_dir) if re.match(r"^g\d+$", d)])
    if points and point != points[-1]:
        blockers.append(
            f"[CHAIN BREAK] Estas validando {point}, pero existen rondas posteriores {points}. "
            "PROHIBIDO editar un golden intermedio sin reset o Rerun from edited golden."
        )
    return blockers


def check_golden(md_path: str, view_path: str, patch_empty: bool):
    with open(md_path, encoding="utf-8") as f:
        text = f.read()
    view_text = ""
    if os.path.exists(view_path):
        with open(view_path, encoding="utf-8", errors="ignore") as vf:
            view_text = vf.read()
    lines = text.splitlines()
    d15_cap = math.ceil((len(text) * 1.1) / 100.0) * 100
    truncated_files = find_truncated_files_in_view(view_path)

    blockers = []
    warnings = []
    in_relevant_files = False

    for idx, line in enumerate(lines, 1):
        s = line.strip()
        if s.lower().startswith("## relevant files"):
            in_relevant_files = True
            continue
        elif s.startswith("## "):
            in_relevant_files = False

        if not (s.startswith("- ") or re.match(r"^\d+\.\s", s)):
            continue

        # 1. Meta-referencias (BLOCKER)
        if GOLDEN_META_PATTERN.search(s):
            blockers.append(f"[Golden L{idx} | C3.1/C3.2] Meta-referencia prohibida al proceso: {s[:105]}")

        # 2. Numeros de linea (BLOCKER)
        if re.search(r"\bat line \d+\b", s, re.I):
            blockers.append(f"[Golden L{idx} | D1.7] Cita numero de linea fragil: {s[:105]}")

        # 3. Patrones compuestos fuertes (BLOCKER / WARNING)
        for pat, msg in GOLDEN_COMPOUND_PATTERNS:
            if re.search(pat, s, re.I):
                blockers.append(f"[Golden L{idx}] {msg}: {s[:95]}")

        # 3b. Decisiones sin justificacion (C2.6 BLOCKER) fuera de Relevant Files
        if not in_relevant_files and BARE_DECISION_PATTERN.search(s) and not RATIONALE_MARKER_PATTERN.search(s):
            blockers.append(f"[Golden L{idx} | C2.6] Decision sin razon explicita ('because/since/outside scope/pre-existing'): {s[:100]}")

        # 4. ';' en prosa (fuera de codigo C++ entre backticks)
        no_code = re.sub(r"`[^`]+`", "", s)
        if ";" in no_code:
            warnings.append(f"[Golden L{idx} | C3.3] Punto y coma ';' fuera de backticks (posible 2 hechos): {s[:100]}")

        # 5. Relevant Files con 2 cosas unidas por 'and' o mezclando tamanio/estado 'unread'/'to finish reading' + rol
        if in_relevant_files:
            if re.search(r"\band\b", no_code, re.I):
                warnings.append(f"[Golden L{idx} | C3.3] Relevant Files usa 'and' (verificar si une 2 componentes/metodos): {s[:100]}")
            if re.search(r"\b\d+-line\b|\bunread\b.*\b(?:module|file)\b|\bto finish reading\b", no_code, re.I):
                blockers.append(f"[Golden L{idx} | C3.3] Relevant Files mezcla tamanio/estado ('N-line'/'unread'/'to finish reading') con rol del archivo: {s[:100]}")

        # 6. 'confirmed' sobre archivos truncados (WARN para verificar si el metodo exacto aparecio antes del corte)
        if "confirmed" in s.lower():
            hit_trunc = [tf for tf in truncated_files if tf in s]
            if hit_trunc:
                warnings.append(f"[Golden L{idx} | C1.3/C2.3] Dice 'confirmed' sobre archivo con [truncated] en view.txt ({hit_trunc}) — verificar que el metodo exacto este visible antes del corte: {s[:90]}")
            else:
                warnings.append(f"[Golden L{idx} | C1.3] Dice 'confirmed' (verificar que el metodo especifico este visible en view.txt): {s[:90]}")

        # 7. Listas de 3+ backticks o pares `A` and `B` (sin eximir palabras comunes como 'to'/'with'/'on')
        if re.search(r"`[^`]+`,\s*`[^`]+`,\s*(?:and\s+)?`[^`]+`", s):
            warnings.append(f"[Golden L{idx} | C3.3] Lista 3+ simbolos en un bullet (revisar atomicidad): {s[:95]}")
        elif re.search(r"`[^`]+`\s+and\s+`[^`]+`", s) and not re.search(r"\b(?:between|such as)\s+`[^`]+`\s+and\s+`[^`]+`", s, re.I):
            warnings.append(f"[Golden L{idx} | C3.3] Par '`A` and `B`' en un bullet (revisar si son 2 hechos): {s[:95]}")

        # 8. Supuestos no verificados que pueden chocar con tail.txt (C2.2 WARN)
        if re.search(r"\b(?:assumed|belief that|remains unverified)\b", s, re.I):
            warnings.append(f"[Golden L{idx} | C2.2] Supuesto/creencia no verificada (revisar tail.txt por posible contradiccion): {s[:95]}")

        # 9. C1.1/C1.2: Verificar identificadores en backticks contra view.txt (bloquea fugas de tail.txt como gslc_Init)
        if view_text:
            for tok in re.findall(r"`([^`]+)`", s):
                # Class.method (no file extensions like .py/.cc/.h/.dbc/.proto/.tpl/.yml/.bzl/.json/.md)
                if re.match(r"^[A-Z][A-Za-z0-9_]*\.[A-Za-z_][A-Za-z0-9_]*$", tok) and tok not in view_text:
                    blockers.append(f"[Golden L{idx} | C1.1] Identificador compuesto `{tok}` NO aparece literalmente en view.txt")
                # Subscript expression like frame[byte] when view uses frame[byte_index]
                for arr_expr in re.findall(r"\b[a-z_][a-z0-9_]*\[[a-z_][a-z0-9_]*\]", tok):
                    if arr_expr not in view_text:
                        blockers.append(f"[Golden L{idx} | C1.2] Expresion `{arr_expr}` NO aparece literalmente en view.txt")
                # Cualquier simbolo de codigo con '_' o CamelCase dentro de backticks debe existir en view.txt
                for sym in re.findall(r"\b[A-Za-z_][A-Za-z0-9_]{3,}\b", tok):
                    if ("_" in sym or (re.search(r"[a-z][A-Z]", sym) and sym[0].isupper())) and not re.search(r"\b" + re.escape(sym) + r"\b", view_text):
                        blockers.append(f"[Golden L{idx} | C1.1/C1.2] Simbolo `{sym}` NO existe en view.txt (posible fuga de tail.txt o invento)")

    print(f"=== [1] GOLDEN SUMMARY ({md_path}) ===")
    print(f"  Chars: {len(text)} | Lines: {len(lines)} | D1.5 expected cap: {d15_cap}")
    if truncated_files:
        print(f"  Archivos [truncated] detectados en view.txt: {sorted(truncated_files)}")
    print(f"  Blockers: {len(blockers)} | Warnings: {len(warnings)}")
    for b in blockers:
        print(f"  [BLOCKER] {b}")
    for w in warnings[:20]:
        print(f"  [WARN]    {w}")
    return text, d15_cap, blockers, warnings, truncated_files


def estimate_task_echo(criteria, instr_path: str):
    """Estima que criterios positivos pueden satisfacerse leyendo solo instruction.md."""
    if not os.path.exists(instr_path):
        return None
    with open(instr_path, encoding="utf-8", errors="ignore") as f:
        instr_text = f.read().lower()
    instr_tokens = set(re.findall(r"[a-zA-Z0-9_]{3,}", instr_text))

    stop = {
        "states", "that", "records", "names", "specifies", "identifies", "explains",
        "the", "for", "with", "from", "into", "when", "must", "agent", "and", "are",
        "not", "all", "its", "each", "only", "can", "per", "has", "have", "been",
        "planned", "pending", "step", "next", "file", "files", "code", "returns",
    }

    pos = [c for c in criteria if c["metadata"]["weight"] in ("major", "minor")]
    total_w = sum(2 if c["metadata"]["weight"] == "major" else 1 for c in pos)
    echo_w = 0
    echo_ids = []

    for c in pos:
        cat = c["metadata"]["category"]
        w = 2 if c["metadata"]["weight"] == "major" else 1
        desc_low = c["description"].lower()
        # Goal fidelity criteria are almost always task-echo; also check high token overlap with instruction.md
        if cat == "Goal fidelity":
            echo_w += w
            echo_ids.append(c["criteria_id"])
            continue
        if cat in ("Compression efficiency", "Temporal coherence"):
            continue
        toks = {t for t in re.findall(r"[a-zA-Z0-9_]{3,}", desc_low) if t not in stop}
        if toks:
            in_instr = len(toks & instr_tokens) / len(toks)
            if in_instr >= 0.85 and "agent" not in desc_low and "inferred" not in desc_low and "unverified" not in desc_low:
                echo_w += w
                echo_ids.append(c["criteria_id"])

    pct = (echo_w / total_w * 100.0) if total_w else 0.0
    return echo_w, total_w, pct, echo_ids


def extract_tool_results_text(view_path: str) -> str:
    if not os.path.exists(view_path):
        return ""
    with open(view_path, encoding="utf-8", errors="ignore") as f:
        text = f.read()
    rows = re.split(r"(?m)^(?=\[\d+\] )", text)
    tool_chunks = []
    for r in rows:
        if "toolResult:" in r[:80] or ("[tool:" not in r[:80] and "assistant:" not in r[:80] and "user:" not in r[:80]):
            tool_chunks.append(r)
        elif "[tool:" in r:
            # OpenCode format: tool outputs appear inline after each [tool:...] line inside assistant rows
            parts = re.split(r"(?m)^\[tool:[^\n]+\n", r)
            for part in parts[1:]:
                tool_chunks.append(part)
    return "\n".join(tool_chunks)


def check_rubric(rubric_path: str, d15_cap: int, golden_text: str, instr_path: str, patch_empty: bool, truncated_files=None, view_path: str = ""):
    truncated_files = truncated_files or set()
    tool_results_text = extract_tool_results_text(view_path)
    full_view_text = ""
    if view_path and os.path.exists(view_path):
        with open(view_path, encoding="utf-8", errors="ignore") as vf:
            full_view_text = vf.read()
    with open(rubric_path, encoding="utf-8") as f:
        data = json.load(f)
    criteria = data.get("criteria", [])

    pos = [c for c in criteria if c["metadata"]["weight"] in ("major", "minor")]
    maj = [c for c in pos if c["metadata"]["weight"] == "major"]
    neg = [c for c in criteria if c["metadata"]["weight"] == "negative"]
    cats = {c["metadata"]["category"] for c in criteria}

    maj_pct = (len(maj) / len(pos) * 100.0) if pos else 0.0

    blockers = []
    warnings = []

    # D1.4 Major ratio
    if not (25.0 <= maj_pct <= 40.0):
        blockers.append(f"[Rubric | D1.4] Major ratio {maj_pct:.1f}% fuera del rango 25%-40% ({len(maj)}/{len(pos)})")
    elif maj_pct < 27.0 or maj_pct > 37.0:
        warnings.append(f"[Rubric | D1.4] Major ratio {maj_pct:.1f}% muy cerca del borde (ideal 28%-35%)")

    # 6 categorias y 3 negativos
    missing_cats = REQUIRED_CATEGORIES - cats
    if missing_cats:
        blockers.append(f"[Rubric | D1.x] Faltan categorias obligatorias: {sorted(missing_cats)}")
    if len(neg) < 3:
        warnings.append(f"[Rubric | D1.9] Se recomiendan 3 criterios negative (actual: {len(neg)})")

    # D1.5 Compression efficiency
    comp_crit = [c for c in criteria if c["metadata"]["category"] == "Compression efficiency"]
    if not comp_crit:
        blockers.append("[Rubric | D1.5] Falta criterio de categoria 'Compression efficiency'")
    else:
        desc = comp_crit[0]["description"]
        expected = f"Contains at most {d15_cap} characters."
        if desc.strip() != expected:
            blockers.append(f"[Rubric | D1.5] Dice '{desc}', esperado exactamente '{expected}'")
        comp_idx = criteria.index(comp_crit[0])
        comp_part = {1: "Part 1", 2: "Part 2", 3: "Part 3", 0: "Part 4"}[comp_idx % 4]
        if comp_part == "Part 3":
            blockers.append(f"[Rubric | {comp_crit[0]['criteria_id']} | D2.3/Part3] Compression efficiency cae en Part 3 (idx%4==3): mover a Part 4 (idx%4==0) para evitar falso positivo D2.3")

    # D2.4 Task-echo
    echo_info = estimate_task_echo(criteria, instr_path)
    if echo_info:
        echo_w, total_w, echo_pct, echo_ids = echo_info
        if echo_pct >= 25.0:
            warnings.append(f"[Rubric | D2.4] Task-echo estimado {echo_w}/{total_w} ({echo_pct:.1f}%) >= 25% -> {echo_ids}")

    # Revision por criterio
    for i, c in enumerate(criteria):
        cid = c["criteria_id"]
        desc = c["description"]
        w = c["metadata"]["weight"]
        cat = c["metadata"]["category"]
        low = desc.lower()
        part = {1: "Part 1", 2: "Part 2", 3: "Part 3", 0: "Part 4"}[i % 4]

        # ID secuencial
        if cid != f"criteria_{i}":
            blockers.append(f"[Rubric | {cid}] ID no secuencial (esperado criteria_{i})")

        # Prohibidos D1.6 / D1.7
        for pat, msg in FORBIDDEN_RUBRIC_PHRASES:
            if re.search(pat, low):
                blockers.append(f"[{cid} | {part}] {msg} -> '{desc[:85]}'")

        # Referentes vagos D2.3 / plurales D2.1
        for pat, msg in VAGUE_RUBRIC_REFERENTS:
            if re.search(pat, low):
                blockers.append(f"[{cid} | {part}] {msg} -> '{desc[:85]}'")

        # Ambiguedad aritmetica / lexica D2.2
        for pat, msg in AMBIGUOUS_MATH_PATTERNS:
            if re.search(pat, low):
                blockers.append(f"[{cid} | {part}] {msg} -> '{desc[:85]}'")

        # Si gNN_state.patch esta vacio, ningun criterio positivo debe afirmar edicion ya hecha o en presente activo
        if patch_empty and w in ("major", "minor") and COMPLETED_EDIT_VERBS.search(low):
            if not PLANNED_EDIT_QUALIFIERS.search(low):
                blockers.append(f"[{cid} | {part} | Criterion truth D2.6] Patch vacio pero criterio describe cambio como codigo actual/completado: '{desc[:90]}'")

        # D2.6: archivos truncados en view.txt o comportamiento C++ generado no mostrado no pueden afirmarse como hecho sin calificador
        if w in ("major", "minor") and not TRUNC_TRUTH_QUALIFIERS.search(low):
            hit_trunc = [tf for tf in truncated_files if tf in desc and tf not in ("apollo_demo.dbc", "demo.proto", "throttle_command_100.cc", "protocol_data.h")]
            if hit_trunc:
                # Si el criterio nombra una funcion especifica (archivo::func) visible en toolResult de view.txt, bajar a WARN
                fn_matches = re.findall(r"::([A-Za-z_][A-Za-z0-9_]*)", desc)
                sym_matches = [t for t in re.findall(r"`([A-Za-z_][A-Za-z0-9_]*)`", desc) if len(t) > 4]
                check_syms = fn_matches or sym_matches
                visible_in_tool = bool(check_syms) and all(s in tool_results_text for s in check_syms)
                if visible_in_tool:
                    warnings.append(f"[{cid} | {part} | Criterion truth D2.6] Archivo {hit_trunc} tuvo algun corte [truncated] en view.txt (simbolo {check_syms} visible en toolResult — verificar que su cuerpo completo aparezca): '{desc[:80]}'")
                else:
                    blockers.append(f"[{cid} | {part} | Criterion truth D2.6] Afirma comportamiento de archivo truncado {hit_trunc} sin calificador (inferred/reasoned/planned): '{desc[:85]}'")
            elif re.search(r"\bmirroring\s+c\+\+\s+`?boundedvalue`?\b", low):
                blockers.append(f"[{cid} | {part} | Criterion truth D2.6] Afirma comportamiento C++ generado no mostrado sin calificar como decision razonada del agente: '{desc[:85]}'")

        # D2.5 Underweighted success criteria o next steps
        if w == "minor":
            if cat == "Goal fidelity" and re.search(r"\b(unchanged|must not change|must match|must preserve|less than)\b", low):
                blockers.append(f"[{cid} | D2.5] Criterio de exito explicito con peso 'minor' (subir a 'major'): '{desc[:85]}'")
            if cat == "Temporal coherence" and re.search(r"\b(next step|pending step|remains open|unfinished|must follow|pending repair)\b", low):
                blockers.append(f"[{cid} | D2.5] Next step con peso 'minor' (subir a 'major'): '{desc[:85]}'")

        # D2.1 pares con 'and' en criterios positivos -> BLOCKER (salvo 'between')
        if w in ("major", "minor"):
            if re.search(r"`[^`]+`\s+and\s+`[^`]+`", desc) and "between" not in low:
                blockers.append(f"[{cid} | {part} | D2.1] Une dos simbolos independientes con 'and' en un criterio: '{desc[:90]}'")
            if re.search(r"\bto add\b.*\band drop\b|\byields\b.*\band will be\b|\bwith the agent noting\b", low):
                blockers.append(f"[{cid} | {part} | D2.1] Combina dos hechos independientes: '{desc[:90]}'")
            if re.search(r"\bround-trips against\b", low):
                blockers.append(f"[{cid} | {part} | D2.2] Frase ambigua 'round-trips against' sin especificar comparacion exacta: '{desc[:90]}'")
            # D2.3: funcion file.py::func sin ruta de directorio completa
            if re.search(r"`[A-Za-z0-9_-]+\.(?:py|cc|cpp|h|hpp)::[A-Za-z0-9_]+`", desc):
                warnings.append(f"[{cid} | {part} | D2.3] Referente archivo::funcion sin ruta completa del repo: '{desc[:90]}'")
            # Criterion truth (v2.7): todo simbolo con '_' o CamelCase en backticks debe existir en view.txt
            if full_view_text:
                for tok in re.findall(r"`([^`]+)`", desc):
                    for sym in re.findall(r"\b[A-Za-z_][A-Za-z0-9_]{3,}\b", tok):
                        if ("_" in sym or (re.search(r"[a-z][A-Z]", sym) and sym[0].isupper())) and not re.search(r"\b" + re.escape(sym) + r"\b", full_view_text):
                            blockers.append(f"[{cid} | {part} | Criterion truth] Simbolo `{sym}` NO existe en view.txt (posible fuga de tail.txt)")
        elif w == "negative":
            if re.search(r"\band\s+(?:cannot|does not|is not|has not|never|will not|fails to|omits)\b", low):
                blockers.append(f"[{cid} | {part} | D2.1] Criterio negativo combina dos afirmaciones con 'and <negacion>': '{desc[:90]}'")

    # D2.8 Overlap entre criterios positivos (Jaccard + entidades backtick compartidas)
    stop = {"states", "that", "records", "names", "specifies", "identifies", "explains", "the", "for", "with", "from", "into", "when", "must", "agent", "in", "of", "to", "and", "or", "is", "are", "as", "by", "on", "a", "an", "not", "all", "its"}
    pos_info = []
    for c in pos:
        toks = {t for t in re.findall(r"[a-zA-Z0-9_]+", c["description"].lower()) if len(t) > 2 and t not in stop}
        syms = {s.strip() for s in re.findall(r"`([^`]+)`", c["description"]) if len(s.strip()) > 3}
        pos_info.append((c["criteria_id"], c["metadata"]["category"], toks, syms, c["description"]))

    for i1 in range(len(pos_info)):
        for i2 in range(i1 + 1, len(pos_info)):
            id1, cat1, t1, s1, d1 = pos_info[i1]
            id2, cat2, t2, s2, d2 = pos_info[i2]
            if not t1 or not t2:
                continue
            inter = t1 & t2
            jaccard = len(inter) / len(t1 | t2)
            shared_syms = s1 & s2
            if jaccard >= 0.70:
                blockers.append(f"[D2.8 Jaccard {jaccard:.2f}] {id1} ({cat1}) <-> {id2} ({cat2}) altamente duplicados {sorted(inter)[:8]} (eliminar/fusionar uno)")
            elif jaccard >= 0.42:
                warnings.append(f"[D2.8 Jaccard {jaccard:.2f}] {id1} ({cat1}) <-> {id2} ({cat2}) comparten {sorted(inter)[:8]}")
            elif shared_syms and cat1 != cat2 and any(k in "".join(shared_syms).lower() for k in ("build", "dlc", "len", "tensionprofile", "filter_protocol_vars", "apply_patch")):
                warnings.append(f"[D2.8 Cross-Cat Symbol] {id1} ({cat1}) <-> {id2} ({cat2}) comparten {sorted(shared_syms)} (verificar doble puntaje)")

    # D2.7 Verificar que los criterios negative no aparezcan literalmente como frase verdadera en el golden
    golden_low = golden_text.lower()
    for c in neg:
        cid = c["criteria_id"]
        desc = c["description"]
        core = re.sub(r"^(?:states|claims|records)\s+that\s+", "", desc.lower()).strip().rstrip(".")
        if len(core) > 25 and core in golden_low:
            blockers.append(f"[{cid} | D2.7] Criterio NEGATIVE coincide literalmente con una frase del golden!: '{desc[:90]}'")

    print(f"\n=== [2] RUBRIC ({rubric_path}) ===")
    print(f"  Total: {len(criteria)} | Positive: {len(pos)} | Major: {len(maj)} ({maj_pct:.1f}%) | Negative: {len(neg)}")
    if echo_info:
        print(f"  Estimated task-echo weight: {echo_info[0]}/{echo_info[1]} ({echo_info[2]:.1f}%) [Target < 25%]")
    print(f"  Blockers: {len(blockers)} | Warnings: {len(warnings)}")
    for b in blockers:
        print(f"  [BLOCKER] {b}")
    for w in warnings[:20]:
        print(f"  [WARN]    {w}")
    return blockers, warnings


def check_winner(task_dir: str, window: str, point: str):
    rs_path = os.path.join(task_dir, "golden", window, point, "run", "run_stats.json")
    print(f"\n=== [3] ROLLOUT STATUS ({rs_path}) ===")
    if not os.path.exists(rs_path):
        print("  No existe run_stats.json -> Requiere Start Compaction tras aprobar Summary QC.")
        return
    with open(rs_path, encoding="utf-8") as f:
        rs = json.load(f)
    wp = rs.get("winner_passed")
    f2p = rs.get("winner_f2p_rate")
    print(f"  winner_passed={wp} | winner_f2p_rate={f2p} | compaction_count={rs.get('compaction_count')}")
    if wp:
        print("  -> Ya hay rollout ganador. NO presionar Start Compaction si solo ajustas formato/rubrica.")
    else:
        print("  -> Sin ganador. Correr Start Compaction tras aprobar Summary QC.")


def main():
    if len(sys.argv) < 4:
        print("Uso: python precheck.py <task_dir> <window> <point> [--strict]")
        sys.exit(1)
    task_dir, window, point = sys.argv[1:4]
    strict = "--strict" in sys.argv[4:]

    md_path = os.path.join(task_dir, "golden", window, point, f"{point}_compaction.md")
    rubric_path = os.path.join(task_dir, "golden", window, point, f"{point}_compaction_rubric.json")
    view_path = os.path.join(task_dir, "_qc", "views", window, point, "view.txt")
    instr_path = os.path.join(task_dir, "instruction.md")
    patch_path = os.path.join(task_dir, "golden", window, point, f"{point}_state.patch")
    patch_empty = os.path.exists(patch_path) and os.path.getsize(patch_path) == 0

    cb_blockers = check_chain_break_risk(task_dir, window, point)
    for b in cb_blockers:
        print(f"[BLOCKER] {b}")

    golden_text, d15_cap, g_blockers, g_warnings, truncated_files = check_golden(md_path, view_path, patch_empty)
    r_blockers, r_warnings = check_rubric(rubric_path, d15_cap, golden_text, instr_path, patch_empty, truncated_files, view_path)
    check_winner(task_dir, window, point)

    total_blockers = len(cb_blockers) + len(g_blockers) + len(r_blockers)
    total_warnings = len(g_warnings) + len(r_warnings)
    print(f"\n=== RESUMEN GATE: {total_blockers} BLOCKERS | {total_warnings} WARNINGS ===")
    if total_blockers > 0 or (strict and total_warnings > 0):
        print("RESULTADO: FAIL — Corregir antes de hacer Commit en Mercor Studio.")
        sys.exit(2)
    print("RESULTADO: PASS — Listo para Commit en Mercor Studio.")


if __name__ == "__main__":
    main()
