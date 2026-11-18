import os
import json
import re

TASK_DIR = os.path.join(os.getcwd(), "task_74b080f5a1554daaba2595c070f210f7", "model_a")
JSON_PATH = os.path.join(TASK_DIR, "steps_structured.json")

with open(JSON_PATH, "r", encoding="utf-8") as f:
    steps = json.load(f)

# Collect all code blocks, file contents, diffs, and patches
file_snippets = []
for s in steps:
    out = s.get("output", "")
    inp = s.get("input", "")
    combined = inp + "\n" + out
    
    # Check if there is a file path and content
    paths = re.findall(r'<path>(.*?)</path>', combined)
    contents = re.findall(r'<content>\s*\n(.*?)(?=\n</content>|\nShow less|\nShow \d+ more lines|\Z)', combined, re.DOTALL)
    
    for i in range(min(len(paths), len(contents))):
        file_snippets.append({
            "step": s["step"],
            "path": paths[i],
            "content": contents[i].strip()
        })

print(f"Total file snippets extracted: {len(file_snippets)}")

# Deduplicate by path, keeping latest or all
snippets_by_file = {}
for snip in file_snippets:
    p = snip["path"]
    if p not in snippets_by_file:
        snippets_by_file[p] = []
    snippets_by_file[p].append(snip)

out_file = os.path.join(TASK_DIR, "ARCHIVOS_Y_CODIGO_GENERADO_A.md")
with open(out_file, "w", encoding="utf-8") as f:
    f.write("# ARCHIVOS GENERADOS Y LÍNEAS DE CÓDIGO - AGENTE A (MODEL A)\n\n")
    f.write("**Tarea:** `bazelbuild-bazel-21177 [model A/B]`  \n")
    f.write("**Repositorio:** `bazelbuild/bazel`  \n")
    f.write("**Total de archivos modificados/creados:** 15 archivos (+690 / -57 líneas)  \n\n")
    f.write("---\n\n")
    
    f.write("## 1. LISTA DE ARCHIVOS CON FRAGMENTOS Y CÓDIGO EXTRAÍDO\n\n")
    for p in sorted(snippets_by_file.keys()):
        f.write(f"- [`{p}`](#{p.replace('/', '').replace('.', '').lower()})\n")
    f.write("\n---\n\n")

    f.write("## 2. DETALLE DE CÓDIGO POR ARCHIVO\n\n")
    for p, snips in sorted(snippets_by_file.items()):
        f.write(f"### Archivo: `{p}`\n\n")
        f.write(f"*Aparece en {len(snips)} pasos de la trayectoria.*\n\n")
        for s in snips:
            f.write(f"#### Paso {s['step']}:\n")
            f.write("```java\n" if p.endswith('.java') else ("```protobuf\n" if p.endswith('.proto') else "```text\n"))
            f.write(s['content'])
            f.write("\n```\n\n")
        f.write("---\n\n")

    f.write("## 3. SOLUCIÓN FINAL DEL MODELO A (DESCRIPCIÓN TÉCNICA DEL PARCHE)\n\n")
    f.write("""```text
I have updated Bazel's spawn execution logging to properly handle symbolic link outputs and type mismatches:

1. Unresolved symlink outputs:
   - Added symlink_target_path to File and ExecLogEntry.File in spawn.proto.
   - When an output declared as an unresolved symlink exists as a symlink on disk, its target path is captured and logged in actual_outputs.

2. Type mismatch vs missing outputs:
   - Added invalid_path to ExecLogEntry.Output in spawn.proto.
   - When declared file, directory, or symlink outputs exist on disk with an unexpected filesystem type, they are logged as invalid_path in compact logs and omitted from actual_outputs in expanded logs, distinguishing them from truly absent outputs (missing_path).

3. Indirect outputs through symlinks:
   - For declared file and directory outputs that are symbolic links pointing to actual content elsewhere, symlinks are followed to compute file digests or directory contents.
```\n""")

print(f"Guardado {out_file} ({os.path.getsize(out_file)} bytes)")
