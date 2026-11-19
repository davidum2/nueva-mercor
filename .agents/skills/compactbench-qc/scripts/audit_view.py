"""
Auditor forense de view.txt, tail.txt y gNN_state.patch para CompactBench v2.
Genera un mapa exacto de evidencia visible vs truncada vs tail-only para evitar fallos
de C1.1, C1.2, C1.3, C2.1, C2.2, C2.3, C2.6, G24 y D2.6.

Uso:
  python .agents/skills/compactbench-qc/scripts/audit_view.py <task_dir> <window> <point>
"""
import os
import re
import sys


def parse_rows(text: str):
    """Divide view.txt o tail.txt en bloques por encabezado de fila [N]."""
    matches = list(re.finditer(r"(?m)^\[(\d+)\]\s*(.*)$", text))
    rows = []
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        rows.append((int(m.group(1)), m.group(2).strip(), text[start:end]))
    return rows


def analyze_view(view_path: str):
    if not os.path.exists(view_path):
        return {}, set(), set(), []
    with open(view_path, encoding="utf-8", errors="ignore") as f:
        text = f.read()

    rows = parse_rows(text)
    truncated_files = {}   # basename -> list of (row_id, context_snippet)
    full_read_files = set()
    grep_only_files = set()
    decisions = []

    file_re = re.compile(r"([A-Za-z0-9_./-]+\.(?:py|cc|cpp|c|h|hpp|proto|dbc|sh|json|toml|md|tpl|bzl|go|rs|java|ts|js|php))")

    for rid, header, body in rows:
        is_trunc = ("[truncated]" in body) or ("more characters truncated" in body) or ("chars truncated" in body)
        # Split body by tool call / file sections if multiple reads occur in one row
        segments = re.split(r"(?m)(?=^(?:tool:|read|cat |grep |rg |file:|path:|---|\$ ))", body)
        for seg in segments:
            files_in_seg = file_re.findall(seg)
            if not files_in_seg:
                continue
            seg_trunc = ("[truncated]" in seg) or ("more characters truncated" in seg) or ("chars truncated" in seg)
            seg_low = seg.lower()
            is_grep = any(k in seg_low[:200] for k in ("grep", "rg ", "find ", "ls ", "glob"))
            for fp in files_in_seg[:3]:
                bn = os.path.basename(fp)
                if seg_trunc:
                    tail_line = [l.strip() for l in seg.splitlines() if l.strip() and "truncated" not in l.lower()][-2:]
                    truncated_files.setdefault(bn, []).append((rid, " | ".join(tail_line)[:120]))
                elif is_grep:
                    grep_only_files.add(bn)
                else:
                    full_read_files.add(bn)

        # Detect design decisions / settled signatures / constraints in reasoning (G24 / C2.6)
        decision_re = re.compile(
            r"(?i)(?:def __init__|without annotations|annotation-free|settled|plan the code|"
            r"signature|default[s]?\s+to|will leave|leave it|leave .* as-is|leave .* unchanged|max len|not exercised|"
            r"I won't|I'll\s+\w+|I will\s+\w+|should treat|exact match|as-is|"
            r"lowercase|uppercase|instead of|/tmp/|scratch|not in the package|keep it|"
            r"truncate|clamp|overflow|order matters|declaration order|"
            r"pre-existing|not my concern|doesn't ask|outside.*scope|not regenerating|untouched|unchanged|"
            r"keep \w+ing|still emitted|skip protocols?|no direct dep|no dep needed|transitively)"
        )
        for m in decision_re.finditer(body):
            line_start = body.rfind("\n", 0, m.start()) + 1
            line_end = body.find("\n", m.end())
            if line_end == -1:
                line_end = len(body)
            full_line = body[line_start:line_end].strip()
            if len(full_line) > 1500:
                rel = m.start() - line_start
                s_idx = max(0, rel - 450)
                e_idx = min(len(full_line), rel + 650)
                snippet = full_line[s_idx:e_idx]
            else:
                snippet = full_line
            if snippet and not snippet.startswith(("+", "-", "def ", "class ", "#include", "//")):
                decisions.append((rid, snippet))

    # Files that had at least one truncated read
    grep_only_files -= full_read_files
    grep_only_files -= set(truncated_files.keys())
    return truncated_files, full_read_files, grep_only_files, decisions


def analyze_tail(tail_path: str):
    if not os.path.exists(tail_path):
        return 0, []
    with open(tail_path, encoding="utf-8", errors="ignore") as f:
        text = f.read()
    if not text.strip():
        return 0, []
    rows = parse_rows(text)
    highlights = []
    for rid, header, body in rows:
        for m in re.finditer(r"(?i)(?:different dbc|different|turns out|not generated|wrong|mistake|without annotations|annotation-free|plan|verify|synthetic|old|new|signature|default|contradict|actually)", body):
            ls = body.rfind("\n", 0, m.start()) + 1
            le = body.find("\n", m.end())
            if le == -1:
                le = len(body)
            highlights.append((rid, body[ls:le].strip()[:300]))
    return len(text), highlights


def main():
    if len(sys.argv) != 4:
        print("Uso: python audit_view.py <task_dir> <window> <point>")
        sys.exit(1)
    task_dir, window, point = sys.argv[1:4]
    view_path = os.path.join(task_dir, "_qc", "views", window, point, "view.txt")
    tail_path = os.path.join(task_dir, "_qc", "views", window, point, "tail.txt")
    patch_path = os.path.join(task_dir, "golden", window, point, f"{point}_state.patch")

    print(f"=== AUDIT FORENSE: {task_dir} ({window}/{point}) ===")

    # 1. State patch
    if os.path.exists(patch_path):
        plen = os.path.getsize(patch_path)
        print(f"\n[1] STATE PATCH ({point}_state.patch): {plen} bytes")
        if plen == 0:
            print("  -> PATCH VACIO: ningun archivo fue modificado todavia.")
            print("     REGLA C2.1/D2.6: Todo cambio de codigo en golden y rubric debe escribirse en modo PLAN/PENDIENTE, nunca 'is removed'/'was added'.")
        else:
            with open(patch_path, encoding="utf-8", errors="ignore") as f:
                pfiles = re.findall(r"^\+\+\+ b/(.+)$", f.read(), re.M)
            print(f"  -> Archivos realmente modificados: {pfiles}")
    else:
        print(f"\n[1] STATE PATCH: no encontrado ({patch_path})")

    # 2. View analysis
    trunc, full_reads, grep_only, decisions = analyze_view(view_path)
    print(f"\n[2] ARCHIVOS TRUNCADOS EN view.txt ({len(trunc)}) — PROHIBIDO decir 'confirmed' sin calificar:")
    for fn in sorted(trunc.keys()):
        hits = trunc[fn][:2]
        print(f"  - {fn}: rows {[h[0] for h in hits]} | ultimo texto visible: {hits[0][1]}")

    print(f"\n[3] ARCHIVOS SOLO GREP/LS EN view.txt ({len(grep_only)}) — NO decir 'Read <archivo>':")
    print("  ", sorted(grep_only)[:25])

    print(f"\n[4] SENALES DE DECISION / FIRMAS / LIMITES EN view.txt (guardadas en _audit_decisions.txt):")
    seen = set()
    unique_decisions = []
    for rid, snip in decisions:
        key = (rid, snip)
        if key in seen:
            continue
        seen.add(key)
        unique_decisions.append((rid, snip))

    dec_out = os.path.join(task_dir, "_audit_decisions.txt")
    with open(dec_out, "w", encoding="utf-8") as df:
        for rid, snip in unique_decisions:
            df.write(f"[row {rid}] {snip}\n")
    print(f"  Total lineas unicas de decision: {len(unique_decisions)} (archivo: {dec_out})")
    for rid, snip in unique_decisions[:45]:
        print(f"  [row {rid}] {snip}")

    # 3. Tail analysis
    tlen, thighlights = analyze_tail(tail_path)
    print(f"\n[5] TAIL.TXT ({tlen} chars):")
    if tlen == 0:
        print("  -> Sin kept tail (o tail.txt no extraido). Verificar con extract_task.py si el harness es OpenCode/Claude Code/Pi.")
    else:
        print("  -> ATENCION: Hay kept tail. Revisar C2.6/G24 (decisiones asentadas) vs C1.2/C2.1 (no filtrar planes nuevos exclusivos de tail):")
        seen_t = set()
        for rid, snip in thighlights[:20]:
            if snip in seen_t:
                continue
            seen_t.add(snip)
            print(f"  [tail row {rid}] {snip}")


if __name__ == "__main__":
    main()
