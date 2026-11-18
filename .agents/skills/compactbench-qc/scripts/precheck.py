"""
Pre-validacion local reforzada para tareas de CompactBench v2 (Golden + Rubric + Slack Rules).
Uso:
  python .agents/skills/compactbench-qc/scripts/precheck.py <task_dir> <window> <point>
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

FORBIDDEN_RUBRIC_PHRASES = [
    ("at line ", "D1.7: no usar numeros de linea en criterios"),
    ("paragraph", "D1.6/D2.2: no calificar layout (paragraphs)"),
    ("list item", "D1.6/D2.2: no calificar layout (list items)"),
    ("separately from", "Posible D1.6: revisar que no califique layout"),
    ("without reading the whole", "D1.6/D2.2: no calificar layout del resumen"),
    ("command not found", "D1.7: no incluir errores transitorios de herramienta"),
]

GOLDEN_COMPOUND_PATTERNS = [
    (r"^-\s+Read\s+.*,.*", "C3.3: bullet 'Read ...' lista multiples archivos (separar 1 archivo por bullet)"),
    (r"^-\s+Settled the design for\s+.*,.*", "C3.3: bullet 'Settled the design...' une multiples artefactos (separar 1 por bullet)"),
    (r"\bwhile removing\b", "C3.3: une una accion con 'while removing' (separar en 2 bullets/pasos)"),
    (r"\btarget and deps\b|\btarget and .* dependencies\b", "C3.3: une creacion de target BUILD con dependencias (separar)"),
    (r"\bto verify\b.*\band\b", "C3.3: une dos verificaciones distintas en un solo paso ('to verify A and B')"),
    (r"\bskip\b.*\band print\b|\band skip printing\b", "C3.3: une 'skip/wire' con 'print' en un mismo bullet"),
    (r"\band\s+(?:printed|omitted|dropped|added|removed|updated|wired|checked|verified)\b", "C3.3: une dos acciones/resultados con 'and <verbo>' (separar en 2 bullets)"),
    (r"\band\s+(?:print|omit|drop|add|remove|update|wire|check|verify)\b", "C3.3: une dos acciones imperativas con 'and <verbo>' (separar en 2 pasos)"),
]


def find_truncated_files_in_view(view_path: str):
    if not os.path.exists(view_path):
        return set()
    with open(view_path, encoding="utf-8", errors="ignore") as f:
        content = f.read()
    truncated_files = set()
    # Look for file paths near [truncated] markers
    for m in re.finditer(r"([A-Za-z0-9_./-]+\.(?:py|cc|cpp|h|hpp|proto|dbc|sh|json|toml|md))", content):
        start = m.start()
        window = content[start:start + 2500]
        if "[truncated]" in window or "more characters truncated" in window:
            truncated_files.add(os.path.basename(m.group(1)))
    return truncated_files


def check_chain_break_risk(task_dir: str, window: str, point: str):
    win_dir = os.path.join(task_dir, "golden", window)
    if not os.path.isdir(win_dir):
        return
    points = sorted([d for d in os.listdir(win_dir) if re.match(r"^g\d+$", d)])
    if points and point != points[-1]:
        print(f"!!! [ALERTA CHAIN BREAK] Estas inspeccionando {point}, pero existen rondas posteriores: {points}.")
        print("    PROHIBIDO editar un golden que no sea el ultimo sin pedir reset o usar Rerun from edited golden.")


def check_golden(md_path: str, view_path: str):
    with open(md_path, encoding="utf-8") as f:
        text = f.read()
    lines = text.splitlines()
    d15_cap = math.ceil((len(text) * 1.1) / 100.0) * 100
    truncated_files = find_truncated_files_in_view(view_path)

    print(f"=== GOLDEN SUMMARY ({md_path}) ===")
    print(f"  Chars: {len(text)} | Lines: {len(lines)} | D1.5 expected cap: {d15_cap}")

    warnings = []
    for idx, line in enumerate(lines, 1):
        s = line.strip()
        if not (s.startswith("- ") or re.match(r"^\d+\.\s", s)):
            continue
        if ";" in s:
            warnings.append(f"  [L{idx}] C3.3 posible bullet compuesto (';'): {s[:110]}")
        if re.search(r"\bat line \d+", s, re.I):
            warnings.append(f"  [L{idx}] D1.7 cita numero de linea: {s[:110]}")
        for pat, msg in GOLDEN_COMPOUND_PATTERNS:
            if re.search(pat, s, re.I):
                warnings.append(f"  [L{idx}] {msg}: {s[:100]}")
        if "confirmed" in s.lower():
            hit_trunc = [tf for tf in truncated_files if tf in s]
            if hit_trunc:
                warnings.append(f"  [L{idx}] C2.3/D2.6 dice 'confirmed' sobre archivo [truncated] en view.txt ({hit_trunc}): {s[:95]}")
            else:
                warnings.append(f"  [L{idx}] C2.3 dice 'confirmed' (verificar que no dependa de output [truncated]): {s[:95]}")
        if re.search(r"`[^`]+`,\s*`[^`]+`,\s*(and\s+)?`[^`]+`", s):
            warnings.append(f"  [L{idx}] C3.3 lista 3+ simbolos/archivos entre backticks en un bullet: {s[:100]}")
        elif re.search(r"`[^`]+`\s+and\s+`[^`]+`", s) and "between" not in s.lower() and "matches" not in s.lower():
            warnings.append(f"  [L{idx}] C3.3 par '`A` and `B`' en un bullet (revisar si son 2 hechos/metodos): {s[:100]}")

    if warnings:
        print(f"  Warnings ({len(warnings)}):")
        for w in warnings[:30]:
            print(w)
    else:
        print("  OK: sin alertas de C3.3 / C2.3 / D1.7.")
    return text, d15_cap


def check_rubric(rubric_path: str, d15_cap: int, golden_text: str):
    with open(rubric_path, encoding="utf-8") as f:
        data = json.load(f)
    criteria = data.get("criteria", [])

    pos = [c for c in criteria if c["metadata"]["weight"] in ("major", "minor")]
    maj = [c for c in pos if c["metadata"]["weight"] == "major"]
    neg = [c for c in criteria if c["metadata"]["weight"] == "negative"]
    cats = {c["metadata"]["category"] for c in criteria}

    maj_pct = (len(maj) / len(pos) * 100.0) if pos else 0.0
    total_pos_weight = sum(2 if c["metadata"]["weight"] == "major" else 1 for c in pos)
    goal_weight = sum(
        2 if c["metadata"]["weight"] == "major" else 1
        for c in pos
        if c["metadata"]["category"] == "Goal fidelity"
    )
    goal_echo_floor_pct = (goal_weight / total_pos_weight * 100.0) if total_pos_weight else 0.0

    print(f"\n=== RUBRIC ({rubric_path}) ===")
    print(f"  Total: {len(criteria)} | Positive: {len(pos)} | Major: {len(maj)} ({maj_pct:.1f}%) | Negative: {len(neg)}")
    print(f"  Positive weight sum: {total_pos_weight} | Goal fidelity weight share: {goal_weight}/{total_pos_weight} ({goal_echo_floor_pct:.1f}%) [Target task-echo < 25%]")

    errors = []
    if not (25.0 <= maj_pct <= 40.0):
        errors.append(f"  [D1.4] Major ratio {maj_pct:.1f}% fuera de rango 25%-40%")
    if goal_echo_floor_pct >= 25.0:
        errors.append(f"  [D2.4] Peso de Goal fidelity ({goal_echo_floor_pct:.1f}%) >= 25%; reducir task-echo")
    missing_cats = REQUIRED_CATEGORIES - cats
    if missing_cats:
        errors.append(f"  [D1.x] Faltan categorias: {sorted(missing_cats)}")
    if len(neg) < 3:
        errors.append(f"  [D1.9] Se recomiendan 3 criterios negative (actual: {len(neg)})")

    comp_crit = [c for c in criteria if c["metadata"]["category"] == "Compression efficiency"]
    if comp_crit:
        desc = comp_crit[0]["description"]
        if str(d15_cap) not in desc:
            errors.append(f"  [D1.5] Compression efficiency dice '{desc}', esperado 'Contains at most {d15_cap} characters.'")

    for i, c in enumerate(criteria):
        cid = c["criteria_id"]
        desc = c["description"]
        w = c["metadata"]["weight"]
        low = desc.lower()
        part = {1: "Part 1", 2: "Part 2", 3: "Part 3", 0: "Part 4"}[i % 4]

        for phrase, msg in FORBIDDEN_RUBRIC_PHRASES:
            if phrase in low:
                errors.append(f"  [{cid} | {part}] {msg} -> '{desc[:90]}'")

        if w in ("major", "minor"):
            if re.search(r"`[^`]+`\s+and\s+`[^`]+`", desc) and "between" not in low:
                errors.append(f"  [{cid} | {part}] Posible D2.1: une dos simbolos con 'and' -> '{desc[:95]}'")
            if re.search(r"\bto add\b.*\band drop\b|\byields\b.*\band will be\b", low):
                errors.append(f"  [{cid} | {part}] D2.1: une dos hechos independientes -> '{desc[:95]}'")

    # Check lexical overlap between positive criteria (Penalties and pairs D2.8)
    stop = {"states", "that", "records", "names", "specifies", "identifies", "explains", "the", "for", "with", "from", "into", "when", "must", "agent", "in", "of", "to", "and", "or", "is", "are", "as", "by", "on", "a", "an"}
    pos_tokens = []
    for c in pos:
        toks = {t for t in re.findall(r"[a-zA-Z0-9_]+", c["description"].lower()) if len(t) > 2 and t not in stop}
        pos_tokens.append((c["criteria_id"], toks, c["description"]))
    for idx1 in range(len(pos_tokens)):
        for idx2 in range(idx1 + 1, len(pos_tokens)):
            id1, t1, d1 = pos_tokens[idx1]
            id2, t2, d2 = pos_tokens[idx2]
            if not t1 or not t2:
                continue
            inter = t1 & t2
            jaccard = len(inter) / len(t1 | t2)
            if jaccard >= 0.45:
                errors.append(f"  [D2.8 Overlap] {id1} y {id2} comparten alto vocabulario ({jaccard:.2f}: {sorted(inter)})")

    if errors:
        print(f"  Issues/Alerts ({len(errors)}):")
        for e in errors:
            print(e)
    else:
        print("  OK: todos los parametros D1.4/D1.5/D1.6/D1.7/D2.1/D2.4/D2.8 en regla.")


def check_winner(task_dir: str, window: str, point: str):
    rs_path = os.path.join(task_dir, "golden", window, point, "run", "run_stats.json")
    print(f"\n=== ROLLOUT STATUS ({rs_path}) ===")
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
    if len(sys.argv) != 4:
        print("Uso: python precheck.py <task_dir> <window> <point>")
        sys.exit(1)
    task_dir, window, point = sys.argv[1:4]
    md_path = os.path.join(task_dir, "golden", window, point, f"{point}_compaction.md")
    rubric_path = os.path.join(task_dir, "golden", window, point, f"{point}_compaction_rubric.json")
    view_path = os.path.join(task_dir, "_qc", "views", window, point, "view.txt")

    check_chain_break_risk(task_dir, window, point)
    golden_text, d15_cap = check_golden(md_path, view_path)
    check_rubric(rubric_path, d15_cap, golden_text)
    check_winner(task_dir, window, point)


if __name__ == "__main__":
    main()
