import re
import json

def parse_full_trajectory(raw_path, out_json):
    with open(raw_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # Find each step block: from 'Step X\n' to the next 'Step Y\n' or EOF
    # In the raw text, each step starts with:
    # Collapse all (optional at top)
    # Step X
    # +0s ...
    # Step X: Calling 1 tool(s): ...
    # X.1 Input:
    # X.2 Output:
    
    # Split text into step sections
    pattern = r'\n(?=Step \d+\n)'
    chunks = re.split(pattern, text)
    print(f"Total raw chunks: {len(chunks)}")

    steps = []
    for chunk in chunks:
        step_match = re.search(r'^Step\s+(\d+)\b', chunk.strip())
        if not step_match:
            continue
        step_num = int(step_match.group(1))

        # Check for tool name
        tool_match = re.search(r'Calling tool\s+([\w\.\-]+)', chunk)
        tool_name = tool_match.group(1) if tool_match else "unknown"

        # Check for Input
        inp_match = re.search(r'\d+\.1\s*Input:\s*\n(.*?)(?=\n\s*\d+\.2\s*Output:|$)', chunk, re.DOTALL)
        input_data = inp_match.group(1).strip() if inp_match else ""

        # Check for Output
        out_match = re.search(r'\d+\.2\s*Output:\s*\n(.*?)(?=\nShow less|\nStep \d+|$)', chunk, re.DOTALL)
        output_data = out_match.group(1).strip() if out_match else ""

        # Check for thought or response
        resp_match = re.search(r'response\s*\n(.*?)(?=\ntool_call|\n\d+\.1\s*Input:|$)', chunk, re.DOTALL)
        response_text = resp_match.group(1).strip() if resp_match else ""

        steps.append({
            "step": step_num,
            "tool": tool_name,
            "input": input_data,
            "output": output_data,
            "thought": response_text
        })

    # Deduplicate steps by keeping the richest entry for each step_num
    final_steps = {}
    for s in steps:
        num = s['step']
        if num not in final_steps:
            final_steps[num] = s
        else:
            # pick the one with more content
            if len(s['input']) + len(s['output']) > len(final_steps[num]['input']) + len(final_steps[num]['output']):
                final_steps[num] = s

    sorted_steps = [final_steps[k] for k in sorted(final_steps.keys())]
    with open(out_json, 'w', encoding='utf-8') as f:
        json.dump(sorted_steps, f, indent=2, ensure_ascii=False)
    print(f"Parsed {len(sorted_steps)} unique steps saved to {out_json}")
    return sorted_steps

if __name__ == '__main__':
    a = parse_full_trajectory("model_a/all_steps_expanded.txt", "model_a/steps_clean.json")
    b = parse_full_trajectory("model_b/all_steps_expanded.txt", "model_b/steps_clean.json")
