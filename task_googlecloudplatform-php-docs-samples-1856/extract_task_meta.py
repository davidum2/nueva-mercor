import os
import json

DEST_DIR = r"c:\desarrollo\nueva-mercor\task_a6c044440a2b440a9d578ad5c375ad94"

with open(os.path.join(DEST_DIR, "task_api_dump.json"), "r", encoding="utf-8") as f:
    api_data = json.load(f)

t = api_data.get('task', {})
cf = t.get('custom_fields', {})

# Save Prompt
prompt = cf.get('field_task_prompt', '')
with open(os.path.join(DEST_DIR, "prompt.md"), "w", encoding="utf-8") as f:
    f.write(prompt)

# Save Patch A
patch_a = cf.get('field_patch_a', '')
with open(os.path.join(DEST_DIR, "model_a", "patch_a.diff"), "w", encoding="utf-8") as f:
    f.write(patch_a)

# Save Patch B
patch_b = cf.get('field_patch_b', '')
with open(os.path.join(DEST_DIR, "model_b", "patch_b.diff"), "w", encoding="utf-8") as f:
    f.write(patch_b)

# Final answers
ans_a = cf.get('field_final_answer_a', '')
with open(os.path.join(DEST_DIR, "model_a", "final_answer_a.txt"), "w", encoding="utf-8") as f:
    f.write(ans_a)

ans_b = cf.get('field_final_answer_b', '')
with open(os.path.join(DEST_DIR, "model_b", "final_answer_b.txt"), "w", encoding="utf-8") as f:
    f.write(ans_b)

print(f"Prompt length: {len(prompt)}")
print(f"Patch A length: {len(patch_a)} ({len(patch_a.splitlines())} lines)")
print(f"Patch B length: {len(patch_b)} ({len(patch_b.splitlines())} lines)")
print(f"Final Answer A length: {len(ans_a)}")
print(f"Final Answer B length: {len(ans_b)}")

# Inspect existing rubrics or dimensions if any
rubric_count = cf.get('field_rubric_count')
print(f"Existing Rubric Count in custom_fields: {rubric_count}")

# Check task status and history
status_id = t.get('task_status_id')
print(f"Status ID: {status_id}")

history = api_data.get('history', [])
print(f"History entries: {len(history)}")
for h in history[:5]:
    print(f"  {h.get('created_at')}: {h.get('task_status_id')} by {h.get('created_by_user_name')}")

# Check artifact & transcript files URLs
print("\nArtifact Files A:", cf.get('artifact_files_a'))
print("Artifact Files B:", cf.get('artifact_files_b'))
print("Transcript File A:", cf.get('transcript_file_a'))
print("Transcript File B:", cf.get('transcript_file_b'))
