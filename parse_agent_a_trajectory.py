import re
import json
import os

TASK_DIR = os.path.join(os.getcwd(), "task_74b080f5a1554daaba2595c070f210f7", "model_a")
RAW_PATH = os.path.join(TASK_DIR, "all_steps_expanded.txt")

with open(RAW_PATH, "r", encoding="utf-8") as f:
    text = f.read()

# Find bounds of steps
step_matches = list(re.finditer(r'^Step (\d+)\b', text, re.MULTILINE))
print(f"Encontrados {len(step_matches)} marcadores de Step")

steps = []
for i in range(len(step_matches)):
    start = step_matches[i].start()
    end = step_matches[i+1].start() if i + 1 < len(step_matches) else len(text)
    step_num = int(step_matches[i].group(1))
    step_chunk = text[start:end].strip()

    # Parse chunk
    # Extract tool call
    tool_call_match = re.search(r'Calling tool (\w+)', step_chunk)
    tool_name = tool_call_match.group(1) if tool_call_match else "unknown"
    if "final_answer" in step_chunk:
        tool_name = "final_answer"

    # Extract Input
    input_text = ""
    input_match = re.search(r'Input:\s*\n(.*?)(?=\n\s*\d+\.\d+\s+Output:|\n\s*Output:|$)', step_chunk, re.DOTALL)
    if input_match:
        input_text = input_match.group(1).strip()

    # Extract Output
    output_text = ""
    output_match = re.search(r'Output:\s*\n(.*)', step_chunk, re.DOTALL)
    if output_match:
        output_text = output_match.group(1).strip()
    elif not input_text:
        output_text = step_chunk

    # Extract response / thought
    thought_match = re.search(r'response\s*\n(.*?)(?=\ntool_call|\n\d+\.\d+|$)', step_chunk, re.DOTALL)
    thought_text = thought_match.group(1).strip() if thought_match else ""

    steps.append({
        "step": step_num,
        "tool": tool_name,
        "thought": thought_text,
        "input": input_text,
        "output": output_text,
        "raw": step_chunk
    })

# Save JSON
json_path = os.path.join(TASK_DIR, "steps_structured.json")
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(steps, f, indent=2, ensure_ascii=False)
print(f"Guardado steps_structured.json con {len(steps)} pasos.")

# Extract files modified / created
files_touched = set()
for s in steps:
    for path in re.findall(r'<path>(.*?)</path>', s['output']) + re.findall(r'<path>(.*?)</path>', s['input']):
        files_touched.add(path)
    for path in re.findall(r'(?:git diff|patch|cat|vim|nano|touch|sed|echo\s+.*?>>?)\s+([a-zA-Z0-9_\-\./]+\.(?:java|proto|sh|py|txt|json|patch))', s['input'] + "\n" + s['output']):
        files_touched.add(path)

# Generate Markdown
md_path = os.path.join(TASK_DIR, "TRAYECTORIA_COMPLETA_AGENT_A.md")
with open(md_path, "w", encoding="utf-8") as f:
    f.write("# TRAYECTORIA COMPLETA - AGENTE A (MODEL A)\n")
    f.write("**Tarea:** `bazelbuild-bazel-21177 [model A/B]`\n")
    f.write(f"**Total de pasos registrados:** {len(steps)} pasos\n")
    f.write("**Resultado:** Solución completada (15 archivos modificados, +690 / -57 líneas)\n\n")
    f.write("---\n\n")
    
    f.write("## 1. RESUMEN DE ARCHIVOS MODIFICADOS Y GENERADOS\n\n")
    f.write("A lo largo de los 108 pasos, el Agente A interactuó con y modificó los siguientes componentes clave del repositorio Bazel:\n\n")
    for ft in sorted(files_touched):
        f.write(f"- `{ft}`\n")
    f.write("\n---\n\n")

    f.write("## 2. DESGLOSE CRONOLÓGICO PASO A PASO (STEPS 1 A 108)\n\n")
    for s in steps:
        f.write(f"### Paso {s['step']}: Herramienta `{s['tool']}`\n\n")
        if s['thought']:
            f.write(f"**Razonamiento del Agente:**\n> {s['thought']}\n\n")
        
        if s['input'] and s['input'] != "{}":
            f.write("**Entrada / Comando ejecutado:**\n```bash\n")
            f.write(s['input'])
            f.write("\n```\n\n")
        
        if s['output']:
            f.write("**Salida / Código / Resultado:**\n```text\n")
            # If very long, keep complete or formatted
            f.write(s['output'])
            f.write("\n```\n\n")
        
        f.write("---\n\n")

print(f"Guardado TRAYECTORIA_COMPLETA_AGENT_A.md ({os.path.getsize(md_path)} bytes)")
