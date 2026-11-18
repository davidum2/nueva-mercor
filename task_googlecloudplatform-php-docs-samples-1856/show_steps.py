import json

def inspect(path, name):
    with open(path, 'r', encoding='utf-8') as f:
        steps = json.load(f)
    print(f"=== {name} ({len(steps)} steps) ===")
    for s in steps:
        tool = s['tool']
        out_prev = s['output'].replace('\n', ' ')[:80]
        inp_prev = s['input'].replace('\n', ' ')[:80]
        print(f"Step {s['step']:02d}: Tool={tool} | In={inp_prev} | Out={out_prev}")

inspect("model_a/steps_clean.json", "MODEL A")
print("\n" + "="*60 + "\n")
inspect("model_b/steps_clean.json", "MODEL B")
