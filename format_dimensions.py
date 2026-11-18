import json
import os

TASK_DIR = os.path.join(os.getcwd(), "task_74b080f5a1554daaba2595c070f210f7")
DUMP_FILE = os.path.join(TASK_DIR, "task_fiber_dump.json")

with open(DUMP_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

cf = data.get("taskCustomFields", {})

dim_names = {
    2: "Architecture, Modularity & Trade-off Soundness",
    3: "Codebase Conventions & Utility Reuse (Anti-Duplication)",
    4: "Robustness, Safety & API Stability",
    5: "Instruction Following & Scope Discipline",
    6: "Planning, Research & Tool Proficiency",
    7: "Verification & Testing Discipline (Integrity & Hygiene)",
    8: "Intermediate Communication & Risk Explanation",
    9: "Final Summary & Presentation Quality"
}

out_md = os.path.join(TASK_DIR, "DIMENSIONES_Y_JUSTIFICACIONES_PREVIAS.md")

with open(out_md, "w", encoding="utf-8") as f:
    f.write("# EVALUACIÓN PREVIA DE LAS DIMENSIONES Y JUSTIFICACIONES (LADO A vs. LADO B)\n\n")
    f.write("**Tarea:** `bazelbuild-bazel-21177 [model A/B]`  \n")
    f.write("**Proyecto:** Project Anton | SWE Trajectory QC Annotation  \n\n")
    f.write("---\n\n")

    f.write("## RESUMEN DE SCORES FINALES\n\n")
    score_a = cf.get("field_ta_final_quality_score_a", "N/A")
    score_b = cf.get("field_ta_final_quality_score_b", "N/A")
    f.write(f"- **Final Quality Score - Lado A:** `{score_a}` / 5\n")
    f.write(f"- **Final Quality Score - Lado B:** `{score_b}` / 5\n\n")

    f.write("### Tabla Comparativa de Scores por Dimensión\n\n")
    f.write("| Dimensión | Nombre de la Dimensión | Score Lado A | Score Lado B |\n")
    f.write("|:---:|---|:---:|:---:|\n")
    for d in range(2, 10):
        s_a = cf.get(f"field_ta_dim{d}_score_a", "N/A")
        s_b = cf.get(f"field_ta_dim{d}_score_b", "N/A")
        f.write(f"| **Dim {d}** | {dim_names[d]} | **{s_a}** | **{s_b}** |\n")
    f.write("\n---\n\n")

    f.write("## DETALLE DE CADA DIMENSIÓN: SCORE Y JUSTIFICACIÓN\n\n")
    for d in range(2, 10):
        name = dim_names[d]
        s_a = cf.get(f"field_ta_dim{d}_score_a", "N/A")
        r_a = cf.get(f"field_ta_dim{d}_reason_a", "N/A")
        s_b = cf.get(f"field_ta_dim{d}_score_b", "N/A")
        r_b = cf.get(f"field_ta_dim{d}_reason_b", "N/A")

        f.write(f"### Dimensión {d}: {name}\n\n")
        f.write(f"#### Lado A (Model A) - Score: **{s_a}** / 5\n")
        f.write(f"> {r_a}\n\n")
        f.write(f"#### Lado B (Model B) - Score: **{s_b}** / 5\n")
        f.write(f"> {r_b}\n\n")
        f.write("---\n\n")

    # Also add Comparative Rationale / Complexity Rationale if exists
    if "field_complexity_rationale" in cf:
        f.write("### Complexity Rationale\n\n")
        f.write(f"> {cf['field_complexity_rationale']}\n\n")
        f.write("---\n\n")

    if "field_adj_rationale" in cf:
        f.write("### Adjudication Rationale (Reviewer Feedback)\n\n")
        f.write(f"> {cf['field_adj_rationale']}\n\n")

print(f"Guardado {out_md} exitosamente.")
