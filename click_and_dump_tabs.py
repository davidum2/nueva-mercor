import asyncio
import os
from playwright.async_api import async_playwright

TASK_ID = "task_74b080f5a1554daaba2595c070f210f7"
OUTPUT_DIR = os.path.join(os.getcwd(), TASK_ID, "tabs")

async def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9223')
    page = [p for ctx in browser.contexts for p in ctx.pages if 'mercor.com' in p.url][0]

    # Find navigation buttons on the left or top
    nav_tabs = [
        ("tab_a_how_it_works", ["How this task works", "A • How this task works"]),
        ("tab_b_task_bundle", ["Task bundle", "B • Task bundle"]),
        ("tab_c_agent_a", ["Agent solution A", "1 • Agent solution A"]),
        ("tab_d_agent_b", ["Agent solution B", "1 • Agent solution B"]),
        ("tab_e_rubrics", ["Rubric (create)", "Rubric", "Rubrics"]),
        ("tab_g_autoqc", ["Deliverable AutoQC", "AutoQC"]),
        ("tab_h_feedback", ["Reviewer Feedback"])
    ]

    for filename, matchers in nav_tabs:
        print(f"Buscando tab para: {filename}...")
        clicked = await page.evaluate(f'''(matchers) => {{
            const btns = Array.from(document.querySelectorAll('button, [role="tab"], div'));
            for (let m of matchers) {{
                const target = btns.find(b => b.innerText && b.innerText.trim() === m);
                if (target) {{
                    target.click();
                    return m;
                }}
            }}
            return null;
        }}''', matchers)
        
        print(f"  -> Clicked: {clicked}")
        await asyncio.sleep(2.0)
        
        # Capture text of the main content
        content = await page.evaluate('document.body.innerText')
        with open(os.path.join(OUTPUT_DIR, f"{filename}.txt"), "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  -> Guardado {filename}.txt ({len(content)} chars)")

if __name__ == "__main__":
    asyncio.run(main())
