with open('task_74b080f5a1554daaba2595c070f210f7/model_b/page_when_model_b_active.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

import re
steps = set()
for l in lines:
    m = re.search(r'Step (\d+)', l)
    if m:
        steps.add(int(m.group(1)))

print("Model B total steps:", len(steps), "max step:", max(steps) if steps else 0)

# Check Final Answer
for i, l in enumerate(lines):
    if 'FINAL ANSWER' in l:
        print(f"Final Answer at line {i}:")
        for j in range(i, min(len(lines), i+15)):
            print(lines[j].strip())
        break
