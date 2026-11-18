import re
import json
import os

TASK_DIR = r"c:\desarrollo\nueva-mercor\task_googlecloudplatform-php-docs-samples-1856"

def parse_model_steps(raw_text_path, out_json_path):
    with open(raw_text_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Find where steps begin and end
    # Match: "Step <num>"
    step_matches = list(re.finditer(r'^Step\s+(\d+)\b', text, re.MULTILINE))
    print(f"[{raw_text_path}] Found {len(step_matches)} Step markers.")

    steps = []
    for i in range(len(step_matches)):
        start = step_matches[i].start()
        end = step_matches[i+1].start() if i + 1 < len(step_matches) else len(text)
        step_num = int(step_matches[i].group(1))
        step_chunk = text[start:end].strip()

        # Stop if we hit evaluation dimensions or other UI elements
        if "Part 3: Process" in step_chunk or "RUBRIC" in step_chunk or "Dimension 5:" in step_chunk:
            # truncate chunk at that point
            for stop_marker in ["Part 3: Process", "RUBRIC", "Dimension 5:", "1 · AGENT SOLUTION"]:
                if stop_marker in step_chunk:
                    step_chunk = step_chunk.split(stop_marker)[0].strip()

        # Extract tool call
        tool_call_match = re.search(r'Calling tool\s+([\w\.\-]+)', step_chunk)
        tool_name = tool_call_match.group(1) if tool_call_match else "unknown"
        if "final_answer" in step_chunk.lower():
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

        # Extract command if terminal
        cmd = ""
        if "terminal" in tool_name or "command" in input_text:
            cmd_match = re.search(r'"command":\s*"([^"]+)"', input_text)
            if cmd_match:
                cmd = cmd_match.group(1)
            else:
                # check if there's raw command
                cmd_raw = re.search(r'(?:bash|sh|cmd|php|composer|git|ls|grep|find|cat)\s+[^\n]+', step_chunk)
                if cmd_raw:
                    cmd = cmd_raw.group(0)

        steps.append({
            "step": step_num,
            "tool": tool_name,
            "command": cmd,
            "input": input_text,
            "output": output_text[:2000],  # trim excessive outputs
            "raw_len": len(step_chunk)
        })

    os.makedirs(os.path.dirname(out_json_path), exist_ok=True)
    with open(out_json_path, "w", encoding="utf-8") as f:
        json.dump(steps, f, indent=2, ensure_ascii=False)
    print(f"Saved {out_json_path} with {len(steps)} steps.")
    return steps

if __name__ == '__main__':
    a_steps = parse_model_steps(
        os.path.join(TASK_DIR, "model_a", "all_steps_expanded.txt"),
        os.path.join(TASK_DIR, "model_a", "steps_structured.json")
    )
    b_steps = parse_model_steps(
        os.path.join(TASK_DIR, "model_b", "all_steps_expanded.txt"),
        os.path.join(TASK_DIR, "model_b", "steps_structured.json")
    )
