import os
import re
import json

TASK_DIR = os.path.join(os.getcwd(), "task_74b080f5a1554daaba2595c070f210f7", "model_b")
INPUT_FILE = os.path.join(TASK_DIR, "page_when_model_b_active.txt")

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    text = f.read()

lines = text.splitlines()

# 1. Identify step boundaries
step_starts = []
for idx, line in enumerate(lines):
    m = re.match(r'^Step (\d+)$', line.strip())
    if m:
        step_num = int(m.group(1))
        if 1 <= step_num <= 66:
            if idx + 1 < len(lines) and ('+0s' in lines[idx+1] or 'step' in lines[idx+1] or '0s' in lines[idx+1]):
                if not any(s['step'] == step_num for s in step_starts):
                    step_starts.append({'step': step_num, 'line_idx': idx})

# End of step 66: where final answer ends or next major heading
end_idx_66 = 2050
for j in range(step_starts[-1]['line_idx'], min(len(lines), step_starts[-1]['line_idx'] + 100)):
    if 'AGENT SOLUTION B' in lines[j] or 'RUBRIC' in lines[j] or '7 FILES CHANGED' in lines[j]:
        end_idx_66 = j
        break

parsed_steps = []
all_file_snippets = []

for i in range(len(step_starts)):
    s_info = step_starts[i]
    step_num = s_info['step']
    start_line = s_info['line_idx']
    end_line = step_starts[i+1]['line_idx'] if i + 1 < len(step_starts) else end_idx_66
    
    chunk_lines = lines[start_line:end_line]
    chunk = "\n".join(chunk_lines)

    # Extract tool call
    tool = "terminal"
    if "final_answer" in chunk:
        tool = "final_answer"
    elif "Calling tool" in chunk:
        m = re.search(r'Calling tool (\w+)', chunk)
        if m:
            tool = m.group(1)

    # Extract thought / response
    thought = ""
    m_resp = re.search(r'\bresponse\s*\n(.*?)(?=\ntool_call|\n\d+\.\d+|\Z)', chunk, re.DOTALL)
    if m_resp:
        thought = m_resp.group(1).strip()

    # Extract Input
    inp = ""
    m_inp = re.search(r'\d+\.\d+\s+Input:\s*\n(.*?)(?=\n\s*\d+\.\d+\s+Output:|\n\s*Output:|\Z)', chunk, re.DOTALL)
    if m_inp:
        inp = m_inp.group(1).strip()

    # Extract Output
    out = ""
    m_out = re.search(r'\d+\.\d+\s+Output:\s*\n(.*)', chunk, re.DOTALL)
    if m_out:
        out = m_out.group(1).strip()
    elif tool == "final_answer":
        m_fa = re.search(r'final_answer\s*\n(.*)', chunk, re.DOTALL)
        if m_fa:
            out = m_fa.group(1).strip()

    # Extract code files mentioned
    files_in_step = re.findall(r'<path>(.*?)</path>', chunk) + re.findall(r'([a-zA-Z0-9_\-\./]+\.(?:java|proto|sh|py|xml|BUILD))', chunk)
    files_in_step = sorted(list(set(files_in_step)))

    # Check for file content snippets
    paths = re.findall(r'<path>(.*?)</path>', chunk)
    contents = re.findall(r'<content>\s*\n(.*?)(?=\n</content>|\nShow less|\nShow \d+ more lines|\Z)', chunk, re.DOTALL)
    for p_idx in range(min(len(paths), len(contents))):
        all_file_snippets.append({
            "step": step_num,
            "path": paths[p_idx],
            "content": contents[p_idx].strip()
        })

    parsed_steps.append({
        "step": step_num,
        "tool": tool,
        "thought": thought,
        "input": inp,
        "output": out if out else chunk,
        "files_mentioned": files_in_step
    })

print(f"Parsed {len(parsed_steps)} steps for Model B.")
print(f"Extracted {len(all_file_snippets)} file snippets.")

# Save JSON
with open(os.path.join(TASK_DIR, "steps_structured.json"), "w", encoding="utf-8") as f:
    json.dump(parsed_steps, f, indent=2, ensure_ascii=False)

# Phase breakdown for Model B (66 steps)
phases = {
    "1. Exploración Inicial y Análisis de Arquitectura (Pasos 1 - 15)": [],
    "2. Diseño del Clasificador Compartido y Esquema Proto (Pasos 16 - 30)": [],
    "3. Implementación en SpawnLogContext y Contextos (Pasos 31 - 45)": [],
    "4. Refactorización de Pruebas Unitarias (Pasos 46 - 55)": [],
    "5. Verificación con Bazel Test y Entrega Final (Pasos 56 - 66)": []
}

for s in parsed_steps:
    n = s["step"]
    if 1 <= n <= 15:
        phases["1. Exploración Inicial y Análisis de Arquitectura (Pasos 1 - 15)"].append(s)
    elif 16 <= n <= 30:
        phases["2. Diseño del Clasificador Compartido y Esquema Proto (Pasos 16 - 30)"].append(s)
    elif 31 <= n <= 45:
        phases["3. Implementación en SpawnLogContext y Contextos (Pasos 31 - 45)"].append(s)
    elif 46 <= n <= 55:
        phases["4. Refactorización de Pruebas Unitarias (Pasos 46 - 55)"].append(s)
    else:
        phases["5. Verificación con Bazel Test y Entrega Final (Pasos 56 - 66)"].append(s)

# Write Markdown report for Model B
md_path = os.path.join(TASK_DIR, "TRAYECTORIA_COMPLETA_AGENT_B.md")
with open(md_path, "w", encoding="utf-8") as f:
    f.write("# TRAYECTORIA COMPLETA Y AUDITORÍA - AGENTE B (MODEL B)\n\n")
    f.write("**Tarea:** `bazelbuild-bazel-21177 [model A/B]`  \n")
    f.write("**Proyecto:** Project Anton | SWE Trajectory QC Annotation  \n")
    f.write("**Modelo:** Model B  \n")
    f.write(f"**Total de Pasos Ejecutados:** {len(parsed_steps)} pasos  \n")
    f.write("**Resultado Final:** 7 archivos modificados (+20 / -13 líneas de código)  \n\n")
    f.write("---\n\n")

    f.write("## RESUMEN EJECUTIVO DE LA TRAYECTORIA\n\n")
    f.write("El Agente B ejecutó una trayectoria más concisa y quirúrgica de **66 pasos** (frente a los 108 del Agente A), orientada a minimizar cambios invasivos y reutilizar abstracciones existentes:\n\n")
    f.write("1. **Identificación temprana de la arquitectura (Paso 1):** Detectó que no existía `AbstractSpawnLogContext` y que la lógica compartida se ubicaba como métodos estáticos en la interfaz `SpawnLogContext`.\n")
    f.write("2. **Diseño centralizado (`getOutputType`):** Creó un clasificador compartido `getOutputType(output, path)` en `SpawnLogContext.java:137` retornando `FILE / DIRECTORY / UNRESOLVED_SYMLINK / MISSING / INVALID`, evitando duplicar lógica entre `CompactSpawnLogContext` y `ExpandedSpawnLogContext`.\n")
    f.write("3. **Extensión en `spawn.proto`:**\n")
    f.write("   - Añadió `File.symlink_target_path = 4`.\n")
    f.write("   - Añadió `ExecLogEntry.UnresolvedSymlink { path, target_path }`.\n")
    f.write("   - En `ExecLogEntry.Output` añadió `unresolved_symlink_id = 4` y `invalid_output_path = 5`.\n")
    f.write("4. **Sustitución de Tests (Paso 39 y 61):** Sustituyó el test `testDirectoryOutput` por `testFileOutput_wrongType` y validó la suite de pruebas `ExecTests`.\n\n")

    f.write("### Principales Archivos y Componentes Afectados:\n")
    f.write("- `src/main/protobuf/spawn.proto`\n")
    f.write("- `src/main/java/com/google/devtools/build/lib/exec/SpawnLogContext.java`\n")
    f.write("- `src/main/java/com/google/devtools/build/lib/exec/CompactSpawnLogContext.java`\n")
    f.write("- `src/main/java/com/google/devtools/build/lib/exec/ExpandedSpawnLogContext.java`\n")
    f.write("- `src/test/java/com/google/devtools/build/lib/exec/CompactSpawnLogContextTest.java`\n")
    f.write("- `src/test/java/com/google/devtools/build/lib/exec/SpawnLogContextTestBase.java`\n\n")

    f.write("---\n\n")
    f.write("## DESGLOSE DE FASES Y PASOS (1 A 66)\n\n")

    for phase_name, p_steps in phases.items():
        f.write(f"### {phase_name}\n\n")
        for s in p_steps:
            f.write(f"#### Paso {s['step']} (`{s['tool']}`)\n\n")
            if s["thought"]:
                f.write(f"**Razonamiento del Agente:**\n> {s['thought']}\n\n")
            
            if s["files_mentioned"]:
                f.write(f"**Archivos / Símbolos:** `{', '.join(s['files_mentioned'][:5])}`  \n\n")

            if s["input"] and s["input"] != "{}":
                f.write("**Comando / Entrada:**\n```bash\n")
                f.write(s["input"])
                f.write("\n```\n\n")

            if s["output"]:
                f.write("**Salida / Código / Resultado:**\n```text\n")
                f.write(s["output"])
                f.write("\n```\n\n")
            
            f.write("---\n\n")

    f.write("## RESPUESTA FINAL ENTREGADA POR EL AGENTE B (PASO 66)\n\n")
    f.write("```text\n")
    f.write(parsed_steps[-1]["output"])
    f.write("\n```\n")

print(f"Guardado TRAYECTORIA_COMPLETA_AGENT_B.md ({os.path.getsize(md_path)} bytes)")

# Write Code and Snippets Markdown for Model B
code_file = os.path.join(TASK_DIR, "ARCHIVOS_Y_CODIGO_GENERADO_B.md")
with open(code_file, "w", encoding="utf-8") as f:
    f.write("# ARCHIVOS GENERADOS Y LÍNEAS DE CÓDIGO - AGENTE B (MODEL B)\n\n")
    f.write("**Tarea:** `bazelbuild-bazel-21177 [model A/B]`  \n")
    f.write("**Repositorio:** `bazelbuild/bazel`  \n")
    f.write("**Total de archivos modificados/creados:** 7 archivos (+20 / -13 líneas)  \n\n")
    f.write("---\n\n")

    snippets_by_file = {}
    for snip in all_file_snippets:
        p = snip["path"]
        if p not in snippets_by_file:
            snippets_by_file[p] = []
        snippets_by_file[p].append(snip)

    f.write("## 1. ARCHIVOS MODIFICADOS Y FRAGMENTOS EXTRAÍDOS\n\n")
    for p in sorted(snippets_by_file.keys()):
        f.write(f"- `{p}` ({len(snippets_by_file[p])} apariciones en la trayectoria)\n")
    f.write("\n---\n\n")

    f.write("## 2. DETALLE DE CÓDIGO Y MODIFICACIONES POR ARCHIVO\n\n")
    for p, snips in sorted(snippets_by_file.items()):
        f.write(f"### Archivo: `{p}`\n\n")
        for s in snips:
            f.write(f"#### Paso {s['step']}:\n")
            f.write("```java\n" if p.endswith('.java') else ("```protobuf\n" if p.endswith('.proto') else "```text\n"))
            f.write(s['content'])
            f.write("\n```\n\n")
        f.write("---\n\n")

    f.write("## 3. SOLUCIÓN FINAL Y PARCHE DEL MODELO B\n\n")
    f.write("""```text
Done. All three gaps are fixed and tests pass.

Changes:
1. src/main/protobuf/spawn.proto:
   - File.symlink_target_path = 4: target of an unresolved symlink output (expanded format).
   - New ExecLogEntry.UnresolvedSymlink { path, target_path }, wired into the top-level payload oneof.
   - ExecLogEntry.Output gained unresolved_symlink_id = 4 and invalid_output_path = 5, the latter separating wrong-type outputs from missing_path.

2. SpawnLogContext.java:
   - New shared classifier getOutputType(output, path) returning FILE/DIRECTORY/UNRESOLVED_SYMLINK/MISSING/INVALID (SpawnLogContext.java:137).
   - Matches declared type (ActionInput.isSymlink() / isDirectory()) against disk:
     * Symlink outputs require an actual symlink (isSymbolicLink(), no following).
     * File/directory outputs follow symlinks transparently.
     * Mismatched types become INVALID rather than MISSING.

3. CompactSpawnLogContext.java:
   - Switches on getOutputType: logs UnresolvedSymlink into the table, logs invalid_output_path, or delegates to logFile/logDirectory.

4. ExpandedSpawnLogContext.java:
   - Uses getOutputType: adds actual_outputs with target_path for unresolved symlinks, omits INVALID from actual_outputs, records listed_outputs for both.

5. Tests:
   - CompactSpawnLogContextTest.java & SpawnLogContextTestBase.java:
     * Replaced testDirectoryOutput with testFileOutput_wrongType (covering type mismatch).
     * Added indirection coverage.
```\n""")

print(f"Guardado ARCHIVOS_Y_CODIGO_GENERADO_B.md ({os.path.getsize(code_file)} bytes)")
