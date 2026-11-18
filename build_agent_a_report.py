import os
import re
import json

TASK_DIR = os.path.join(os.getcwd(), "task_74b080f5a1554daaba2595c070f210f7", "model_a")
RAW_PATH = os.path.join(TASK_DIR, "all_steps_expanded.txt")

with open(RAW_PATH, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Extract lines from line 208 to line 3347 (the steps block)
step_lines = lines[208:3347]
full_steps_text = "".join(step_lines)

# Split by "^Step (\d+)\n"
pattern = re.compile(r'^Step (\d+)\n', re.MULTILINE)
splits = list(pattern.finditer(full_steps_text))

print(f"Total step matches: {len(splits)}")

parsed_steps = []
for i in range(len(splits)):
    step_num = int(splits[i].group(1))
    start_pos = splits[i].start()
    end_pos = splits[i+1].start() if i + 1 < len(splits) else len(full_steps_text)
    chunk = full_steps_text[start_pos:end_pos].strip()

    # Extract tool call
    tool = "terminal"
    if "final_answer" in chunk:
        tool = "final_answer"
    elif "Calling tool" in chunk:
        m = re.search(r'Calling tool (\w+)', chunk)
        if m:
            tool = m.group(1)

    # Extract Input
    inp = ""
    m_inp = re.search(r'\d+\.\d+\s+Input:\s*\n(.*?)(?=\n\s*\d+\.\d+\s+Output:|\n\s*Output:|$)', chunk, re.DOTALL)
    if m_inp:
        inp = m_inp.group(1).strip()

    # Extract Output
    out = ""
    m_out = re.search(r'\d+\.\d+\s+Output:\s*\n(.*)', chunk, re.DOTALL)
    if m_out:
        out = m_out.group(1).strip()
    elif "final_answer" in chunk:
        # For final answer, get the text
        m_fa = re.search(r'final_answer\s*\n(.*?)(?=\n\+\d+s|\Z)', chunk, re.DOTALL)
        if m_fa:
            out = m_fa.group(1).strip()

    # Extract files mentioned in output or chunk
    files_in_step = re.findall(r'<path>(.*?)</path>', chunk) + re.findall(r'([a-zA-Z0-9_\-\./]+\.(?:java|proto|sh|py|xml|BUILD))', chunk)
    files_in_step = sorted(list(set(files_in_step)))

    parsed_steps.append({
        "step": step_num,
        "tool": tool,
        "input": inp,
        "output": out,
        "files_mentioned": files_in_step,
        "raw_text": chunk
    })

print(f"Parsed {len(parsed_steps)} steps successfully.")

# Save JSON
with open(os.path.join(TASK_DIR, "steps_structured.json"), "w", encoding="utf-8") as f:
    json.dump(parsed_steps, f, indent=2, ensure_ascii=False)

# Analyze steps by phases
phases = {
    "1. Exploración y Localización del Código (Pasos 1 - 25)": [],
    "2. Modificación de Protocol Buffers y Esquemas (Pasos 26 - 45)": [],
    "3. Implementación en Compact & Expanded SpawnLogContext (Pasos 46 - 75)": [],
    "4. Compilación, Depuración y Ajustes en Tools/Execlog (Pasos 76 - 95)": [],
    "5. Ejecución de Tests, Verificación y Entrega Final (Pasos 96 - 108)": []
}

for s in parsed_steps:
    n = s["step"]
    if 1 <= n <= 25:
        phases["1. Exploración y Localización del Código (Pasos 1 - 25)"].append(s)
    elif 26 <= n <= 45:
        phases["2. Modificación de Protocol Buffers y Esquemas (Pasos 26 - 45)"].append(s)
    elif 46 <= n <= 75:
        phases["3. Implementación en Compact & Expanded SpawnLogContext (Pasos 46 - 75)"].append(s)
    elif 76 <= n <= 95:
        phases["4. Compilación, Depuración y Ajustes en Tools/Execlog (Pasos 76 - 95)"].append(s)
    else:
        phases["5. Ejecución de Tests, Verificación y Entrega Final (Pasos 96 - 108)"].append(s)

# Generate Markdown Document
md_file = os.path.join(TASK_DIR, "TRAYECTORIA_COMPLETA_AGENT_A.md")
with open(md_file, "w", encoding="utf-8") as f:
    f.write("# TRAYECTORIA COMPLETA Y AUDITORÍA - AGENTE A (MODEL A)\n\n")
    f.write("**Tarea:** `bazelbuild-bazel-21177 [model A/B]`  \n")
    f.write("**Proyecto:** Project Anton | SWE Trajectory QC Annotation  \n")
    f.write("**Modelo:** Model A  \n")
    f.write(f"**Total de Pasos Ejecutados:** {len(parsed_steps)} pasos  \n")
    f.write("**Resultado Final:** 15 archivos modificados (+690 / -57 líneas de código)  \n\n")
    f.write("---\n\n")

    f.write("## RESUMEN EJECUTIVO DE LA TRAYECTORIA\n\n")
    f.write("El Agente A ejecutó un enfoque exploratorio exhaustivo de **108 pasos** para resolver los tres problemas planteados en Bazel:\n")
    f.write("1. **Enlaces simbólicos no resueltos (*Unresolved symlinks*):** Añadió `symlink_target_path` en `File` y `ExecLogEntry.File` dentro de `spawn.proto`.\n")
    f.write("2. **Discrepancia de tipos (*Type mismatch* vs. *missing outputs*):** Añadió `invalid_path` en `ExecLogEntry.Output` dentro de `spawn.proto`.\n")
    f.write("3. **Seguimiento de enlaces indirectos:** Modificó la lógica en `CompactSpawnLogContext.java` y `ExpandedSpawnLogContext.java` para seguir symlinks y calcular digests/contenidos.\n\n")
    
    f.write("### Principales Archivos y Componentes Afectados:\n")
    f.write("- `src/main/protobuf/spawn.proto`\n")
    f.write("- `src/main/java/com/google/devtools/build/lib/exec/CompactSpawnLogContext.java`\n")
    f.write("- `src/main/java/com/google/devtools/build/lib/exec/ExpandedSpawnLogContext.java`\n")
    f.write("- `src/main/java/com/google/devtools/build/lib/exec/SpawnLogContext.java`\n")
    f.write("- `src/tools/execlog/src/main/java/com/google/devtools/build/execlog/ExecLogParser.java`\n")
    f.write("- `src/tools/execlog/BUILD`\n")
    f.write("- `src/test/java/com/google/devtools/build/lib/exec/CompactSpawnLogContextTest.java`\n")
    f.write("- `src/test/java/com/google/devtools/build/lib/exec/ExpandedSpawnLogContextTest.java`\n\n")

    f.write("---\n\n")
    f.write("## DESGLOSE DE FASES Y PASOS (1 A 108)\n\n")

    for phase_name, p_steps in phases.items():
        f.write(f"### {phase_name}\n\n")
        for s in p_steps:
            f.write(f"#### Paso {s['step']} (`{s['tool']}`)\n\n")
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
            else:
                f.write("**Detalle:**\n```text\n")
                f.write(s["raw_text"])
                f.write("\n```\n\n")
            f.write("---\n\n")

    f.write("## RESPUESTA FINAL ENTREGADA POR EL AGENTE A (PASO 108)\n\n")
    f.write("```text\n")
    f.write(parsed_steps[-1]["output"])
    f.write("\n```\n")

print(f"Generado exitosamente TRAYECTORIA_COMPLETA_AGENT_A.md ({os.path.getsize(md_file)} bytes)")
