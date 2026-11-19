"""
Inyector seguro con Gate de pre-validacion para Mercor Studio via CDP (puerto 9223).
1. Ejecuta precheck.py y ABORTA si hay BLOCKERS (salvo --force).
2. Inyecta gNN_compaction.md y gNN_compaction_rubric.json en sus modelos Monaco exactos.
3. Hace Commit individual por archivo y verifica 'No unsaved changes'.

Uso:
  python .agents/skills/compactbench-qc/scripts/commit_task.py <task_id> <window> <point> [port] [--only golden|rubric] [--force]
"""
import asyncio
import os
import subprocess
import sys
from playwright.async_api import async_playwright


async def update_and_commit_file(page, task_id: str, rel_path: str, new_text: str):
    btn = page.locator(f'button[title="{rel_path}"]').first
    await btn.click()
    await asyncio.sleep(1.2)

    updated_uris = await page.evaluate(
        """([tid, targetPath, val]) => {
            if (!window.monaco) return [];
            const matched = [];
            for (const m of window.monaco.editor.getModels()) {
                const u = m.uri.toString();
                if (u.includes(tid) && u.endsWith(targetPath)) {
                    m.setValue(val);
                    matched.push(u);
                }
            }
            return matched;
        }""",
        [task_id, rel_path, new_text],
    )
    print(f"  Updated {rel_path}: {updated_uris} (len={len(new_text)})")
    await asyncio.sleep(0.8)

    commit_btn = page.locator('button:has-text("Commit")').first
    if await commit_btn.count() > 0 and await commit_btn.is_enabled():
        print(f"  Clicking Commit for {rel_path}...")
        await commit_btn.click()
        await asyncio.sleep(2.5)
    else:
        print(f"  Commit sin cambios pendientes para {rel_path}")


async def run_commit(task_id: str, window: str, point: str, port: int, only: str = None):
    base = os.path.abspath(task_id)
    rel_md = f"golden/{window}/{point}/{point}_compaction.md"
    rel_rub = f"golden/{window}/{point}/{point}_compaction_rubric.json"

    with open(os.path.join(base, rel_md.replace("/", os.sep)), encoding="utf-8") as f:
        comp_md = f.read()
    with open(os.path.join(base, rel_rub.replace("/", os.sep)), encoding="utf-8") as f:
        rubric_json = f.read()

    p = await async_playwright().start()
    b = await p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
    page = next((pg for ctx in b.contexts for pg in ctx.pages if task_id in pg.url), None)
    if page is None:
        print(f"[ERROR] No se encontro pestana abierta en Studio para {task_id}")
        await p.stop()
        sys.exit(1)

    await page.bring_to_front()
    if only in (None, "golden"):
        await update_and_commit_file(page, task_id, rel_md, comp_md)
    if only in (None, "rubric"):
        await update_and_commit_file(page, task_id, rel_rub, rubric_json)

    txt = await page.evaluate("document.body.innerText")
    print("  NO_UNSAVED_CHANGES:", "No unsaved changes" in txt)
    await p.stop()


def main():
    if len(sys.argv) < 4:
        print("Uso: python commit_task.py <task_id> <window> <point> [port] [--only golden|rubric] [--force]")
        sys.exit(1)
    task_id, window, point = sys.argv[1:4]
    extra = sys.argv[4:]
    force = "--force" in extra
    only = None
    if "--only" in extra:
        oi = extra.index("--only")
        if oi + 1 < len(extra):
            only = extra[oi + 1]
    port_args = [a for a in extra if a.isdigit()]
    port = int(port_args[0]) if port_args else 9223

    precheck = os.path.join(os.path.dirname(__file__), "precheck.py")
    if not force:
        res = subprocess.run([sys.executable, precheck, task_id, window, point])
        if res.returncode != 0:
            print("\n[ABORTADO] precheck.py encontro BLOCKERS. Corrige antes de subir a Studio (o usa --force).")
            sys.exit(res.returncode)

    asyncio.run(run_commit(task_id, window, point, port, only=only))


if __name__ == "__main__":
    main()
