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

patch_a = cf.get('field_patch_a') or ''
with open(os.path.join(TASK_DIR, 'patch_a.diff'), 'w', encoding='utf-8') as f:
    f.write(patch_a)

patch_b = cf.get('field_patch_b') or ''
with open(os.path.join(TASK_DIR, 'patch_b.diff'), 'w', encoding='utf-8') as f:
    f.write(patch_b)

print(f"Saved patch_a.diff ({len(patch_a)} chars, {len(patch_a.splitlines())} lines)")
print(f"Saved patch_b.diff ({len(patch_b)} chars, {len(patch_b.splitlines())} lines)")
