import json

with open('question_bank_50.json', 'r', encoding='utf-8') as f:
    questions = json.load(f)

md_lines = [
    "# Matriz Completa de Evaluación de Trayectorias (50 Preguntas Atómicas)",
    "",
    "**Tarea:** `googlecloudplatform-php-docs-samples-1856`  ",
    "**Model A (Gemini):** `gemini-3.7-flash` (Seeded: PASS)  ",
    "**Model B:** `gpt-5.6-sol` (Seeded: FAIL)  ",
    "",
    "---",
    "",
    "## 1. Resumen Estadístico Global (Banco de 50 Preguntas)",
    "",
    "| Métrica | Model A (Gemini) | Model B (GPT) |",
    "| :--- | :--- | :--- |",
]

a_yes = sum(1 for q in questions if q['expected_a'] == 'YES')
b_yes = sum(1 for q in questions if q['expected_b'] == 'YES')

md_lines.append(f"| **Total Respuestas YES** | **{a_yes} / 50 ({a_yes/50*100:.1f}%)** | **{b_yes} / 50 ({b_yes/50*100:.1f}%)** |")
md_lines.append(f"| **Total Respuestas NO** | **{50 - a_yes} / 50 ({(50 - a_yes)/50*100:.1f}%)** | **{50 - b_yes} / 50 ({(50 - b_yes)/50*100:.1f}%)** |")
md_lines.append("")
md_lines.append("---")
md_lines.append("")
md_lines.append("## 2. Detalle de Evaluación por Pregunta")
md_lines.append("")

current_dim = None
for q in questions:
    if q['dimension'] != current_dim:
        current_dim = q['dimension']
        md_lines.append(f"### Dimensión {current_dim}: {q['dimension_name']}")
        md_lines.append("")

    qid = q['id']
    src = q['source']
    q_text = q['question']
    ans_a = q['expected_a']
    note_a = q['note_a']
    ans_b = q['expected_b']
    note_b = q['note_b']

    badge_a = "🟢 **YES**" if ans_a == "YES" else "🔴 **NO**"
    badge_b = "🟢 **YES**" if ans_b == "YES" else "🔴 **NO**"

    md_lines.append(f"#### `{qid}`: {q_text}")
    md_lines.append(f"- **Fuente:** `{src}`")
    md_lines.append(f"- **Model A ({ans_a}):** {badge_a} — {note_a}")
    md_lines.append(f"- **Model B ({ans_b}):** {badge_b} — {note_b}")
    md_lines.append("")

with open('trajectory_evaluation_matrix.md', 'w', encoding='utf-8') as f:
    f.write('\n'.join(md_lines))

print("Saved trajectory_evaluation_matrix.md successfully.")
