"""
Extractor completo de tareas de CompactBench v2 desde Mercor Studio via CDP (puerto 9223).
Descarga SIEMPRE view.txt, tail.txt, history.txt, instruction.md, harness_compaction.md,
gNN_state.patch, golden, rubric y run_stats.json para auditoria sin puntos ciegos.

Uso:
  python .agents/skills/compactbench-qc/scripts/extract_task.py <task_id> <window> <point> [port]
Ejemplo:
  python .agents/skills/compactbench-qc/scripts/extract_task.py task_5b6365b8b1de4492a09edaf3a1aad92a 128K g01
"""
import asyncio
import os
import sys
from playwright.async_api import async_playwright


async def extract_task(task_id: str, window: str, point: str, port: int = 9223):
    out_dir = os.path.abspath(task_id)
    files_to_extract = [
        "instruction.md",
        "harness_compaction.md",
        "task.toml",
        f"golden/{window}/{point}/{point}_compaction.md",
        f"golden/{window}/{point}/{point}_compaction_rubric.json",
        f"golden/{window}/{point}/{point}_compaction_rubric.md",
        f"golden/{window}/{point}/{point}_baseline_summary.md",
        f"golden/{window}/{point}/{point}_trigger_metadata.json",
        f"golden/{window}/{point}/{point}_state.patch",
        f"golden/{window}/{point}/run/run_stats.json",
        f"_qc/views/{window}/{point}/view.txt",
        f"_qc/views/{window}/{point}/tail.txt",
        f"_qc/views/{window}/{point}/history.txt",
        "solution/solution.patch",
    ]

    p = await async_playwright().start()
    b = await p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
    page = None
    for ctx in b.contexts:
        for pg in ctx.pages:
            if task_id in pg.url:
                page = pg
                break
        if page:
            break

    if page is None:
        print(f"[ERROR] No se encontro pestana abierta en Studio para {task_id}")
        await p.stop()
        sys.exit(1)

    print(f"Extrayendo {task_id} ({window}/{point}) en {out_dir}...")
    for rel_path in files_to_extract:
        btn = page.locator(f'button[title="{rel_path}"]').first
        if await btn.count() == 0:
            print(f"  SKIP (no encontrado en UI): {rel_path}")
            continue
        await btn.click()
        await asyncio.sleep(0.8)

        fname = os.path.basename(rel_path)
        content = None
        for _ in range(12):
            models = await page.evaluate(
                """() => window.monaco
                ? window.monaco.editor.getModels().map(m => ({uri: m.uri.toString(), val: m.getValue()}))
                : []"""
            )
            for m in reversed(models):
                if task_id in m["uri"] and (m["uri"].endswith(rel_path) or fname in m["uri"]):
                    content = m["val"]
                    break
            if content is not None:
                break
            await asyncio.sleep(0.3)

        if content is None:
            print(f"  WARN (sin modelo Monaco): {rel_path}")
            continue

        dest = os.path.join(out_dir, rel_path.replace("/", os.sep))
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  SAVED: {rel_path} ({len(content)} chars)")

    await p.stop()


def main():
    if len(sys.argv) < 4:
        print("Uso: python extract_task.py <task_id> <window> <point> [port]")
        sys.exit(1)
    task_id, window, point = sys.argv[1:4]
    port = int(sys.argv[4]) if len(sys.argv) >= 5 else 9223
    asyncio.run(extract_task(task_id, window, point, port))


if __name__ == "__main__":
    main()
