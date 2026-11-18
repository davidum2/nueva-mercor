import json
import os
import sys

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_ID = 'task_08ccf272669347c3af63de71b2ecb5e5'
TASK_DIR = os.path.join(r'c:\desarrollo\nueva-mercor', f'task_{TASK_ID}')

with open(os.path.join(TASK_DIR, 'task_api.json'), 'r', encoding='utf-8') as f:
    task = json.load(f)

t = task.get('task') or task
cf = t.get('custom_fields', {})

# 1. Save prompt
prompt = cf.get('field_task_prompt') or t.get('prompt') or ''
with open(os.path.join(TASK_DIR, 'prompt.md'), 'w', encoding='utf-8') as f:
    f.write(prompt)
print(f"Saved prompt.md ({len(prompt)} chars)")

# 2. Save final answers
with open(os.path.join(TASK_DIR, 'final_answer_a.txt'), 'w', encoding='utf-8') as f:
    f.write(str(cf.get('field_final_answer_a') or ''))
with open(os.path.join(TASK_DIR, 'final_answer_b.txt'), 'w', encoding='utf-8') as f:
    f.write(str(cf.get('field_final_answer_b') or ''))
print("Saved final_answer_a.txt and final_answer_b.txt")

# 3. Check diffs/patches in custom_fields or artifact files
print("\n=== ARTIFACT FILES ===")
print("artifact_files_a:", cf.get('artifact_files_a'))
print("artifact_files_b:", cf.get('artifact_files_b'))
print("transcript_file_a:", cf.get('transcript_file_a'))
print("transcript_file_b:", cf.get('transcript_file_b'))

# 4. Check ledger
print("\n=== RUN LEDGER ===")
print(cf.get('field_dl_run_ledger'))

# 5. Check all dimensions currently scored
print("\n=== DIMENSION SCORES ===")
for d in range(2, 10):
    sa = cf.get(f'field_ta_dim{d}_score_a')
    ra = cf.get(f'field_ta_dim{d}_reason_a')
    sb = cf.get(f'field_ta_dim{d}_score_b')
    rb = cf.get(f'field_ta_dim{d}_reason_b')
    print(f"Dim {d}: A={sa} | B={sb}")
    print(f"  Reason A: {str(ra)[:100]}")
    print(f"  Reason B: {str(rb)[:100]}")

print("\nQuality Score A:", cf.get('field_ta_final_quality_score_a'))
print("Quality Score B:", cf.get('field_ta_final_quality_score_b'))
print("Comparative Rationale:\n", cf.get('field_1e32bd048d564685ba8ec51f9af11c70'))
