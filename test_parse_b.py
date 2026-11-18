import os
import re
import json

TASK_DIR = os.path.join(os.getcwd(), "task_74b080f5a1554daaba2595c070f210f7", "model_b")
INPUT_FILE = os.path.join(TASK_DIR, "page_when_model_b_active.txt")

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    text = f.read()

lines = text.splitlines()

# Find all occurrences of "Step X"
# Step 1 starts at line 162, Step 66 is around line 2010
step_starts = []
for idx, line in enumerate(lines):
    m = re.match(r'^Step (\d+)$', line.strip())
    if m:
        step_num = int(m.group(1))
        # Filter: only consider steps between 1 and 66, and avoid duplicates if already recorded this step_num
        if 1 <= step_num <= 66:
            # Check if this is the start of a step block (followed by +0s or step numbers)
            if idx + 1 < len(lines) and ('+0s' in lines[idx+1] or 'step' in lines[idx+1] or '0s' in lines[idx+1]):
                # If we don't have this step or if it's the first time
                if not any(s['step'] == step_num for s in step_starts):
                    step_starts.append({'step': step_num, 'line_idx': idx})

print(f"Total unique steps identified: {len(step_starts)}")
for s in step_starts[:10]:
    print(f"Step {s['step']} at line {s['line_idx']}")
print("...")
for s in step_starts[-5:]:
    print(f"Step {s['step']} at line {s['line_idx']}")
