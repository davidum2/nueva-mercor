import json
import re

def summarize(model_name, json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        steps = json.load(f)
    print(f"=== {model_name} ===")
    seen_steps = set()
    for s in steps:
        step_num = s['step']
        if step_num in seen_steps:
            continue
        seen_steps.add(step_num)
        tool = s['tool']
        out_snippet = s['output'].replace('\n', ' ')[:100]
        inp_snippet = s['input'].replace('\n', ' ')[:100]
        print(f"Step {step_num:02d} [{tool}]: In={inp_snippet} | Out={out_snippet}")

if __name__ == '__main__':
    summarize("MODEL A", "model_a/steps_structured.json")
    print("\n" + "="*50 + "\n")
    summarize("MODEL B", "model_b/steps_structured.json")
