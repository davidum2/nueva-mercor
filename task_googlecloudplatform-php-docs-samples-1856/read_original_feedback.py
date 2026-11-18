import json

with open('task_api_dump.json', 'r', encoding='utf-8') as f:
    task = json.load(f)

print("=== FROM task_api_dump.json ===")
cf = task.get('custom_fields', {})
for k in cf:
    if any(w in k.lower() for w in ['adj', 'rationale', 'feedback', 'review', 'note', 'rejection', 'comment']):
        print(f"[{k}]:\n{cf[k]}\n")

for k in task:
    if any(w in k.lower() for w in ['review', 'feedback', 'history', 'note', 'transition']):
        print(f"Task level [{k}]:\n{task[k]}\n")

with open('custom_fields.json', 'r', encoding='utf-8') as f:
    cf_orig = json.load(f)

print("=== FROM custom_fields.json ===")
for k in cf_orig:
    if any(w in k.lower() for w in ['adj', 'rationale', 'feedback', 'review', 'note', 'rejection', 'comment']):
        print(f"[{k}]:\n{cf_orig[k]}\n")
