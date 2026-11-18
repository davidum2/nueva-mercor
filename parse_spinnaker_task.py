import json
import os
import sys

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_08ccf272669347c3af63de71b2ecb5e5'
TASK_DIR = os.path.join(r'c:\desarrollo\nueva-mercor', f'task_{TASK_ID}')

with open(os.path.join(TASK_DIR, 'task_api.json'), 'r', encoding='utf-8') as f:
    task = json.load(f)

print("=== TASK STRUCTURE ===")
print("Task Keys:", list(task.keys()))
if 'task' in task:
    t = task['task']
else:
    t = task

print("Name:", t.get('name'))
print("Status:", t.get('status'))
print("Current stage:", t.get('current_stage'))

# Check custom fields
cf = t.get('custom_fields', {})
print("\n=== CUSTOM FIELDS ===")
for k, v in cf.items():
    if v is not None and str(v).strip() != "":
        val_str = str(v)
        if len(val_str) > 150:
            val_str = val_str[:150] + "..."
        print(f"  {k}: {val_str}")

# Extract Reviewer Feedback and History
print("\n=== ADJUDICATION RATIONALE / REVIEWER FEEDBACK ===")
print(cf.get('field_adj_rationale'))

# Check verifiers
with open(os.path.join(TASK_DIR, 'verifiers_api.json'), 'r', encoding='utf-8') as f:
    verifiers_data = json.load(f)

verifiers = verifiers_data.get('verifiers') or verifiers_data
print(f"\n=== VERIFIERS COUNT: {len(verifiers)} ===")
for i, v in enumerate(verifiers):
    cfv = v.get('verifier_custom_field_values') or {}
    val = v.get('verifier_values') or {}
    print(f"\n--- Verifier #{i+1} (id={v.get('id')}) ---")
    print(f"  Criteria: {val.get('criteria')}")
    print(f"  Dimension: {cfv.get('dimension') or cfv.get('mapped_dimension')}")
    print(f"  Source: {cfv.get('source') or cfv.get('rubric_source')}")
    print(f"  Ans A: {cfv.get('answer_a')} | Ans B: {cfv.get('answer_b')}")
    print(f"  Reason A: {cfv.get('reason_a')}")
    print(f"  Reason B: {cfv.get('reason_b')}")
