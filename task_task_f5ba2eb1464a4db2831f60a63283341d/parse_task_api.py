import json
import os
import sys

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_DIR = r'c:\desarrollo\nueva-mercor\task_task_f5ba2eb1464a4db2831f60a63283341d'

def inspect():
    with open(os.path.join(TASK_DIR, 'task_api.json'), 'r', encoding='utf-8') as f:
        task = json.load(f)

    print("=== TASK TOP LEVEL KEYS ===")
    print(list(task.keys()))

    print("\n=== METADATA ===")
    for k in ['id', 'name', 'status', 'state', 'created_at', 'updated_at', 'assigned_user_id']:
        print(f"  {k}: {task.get(k)}")

    # Prompt / Instructions
    prompt = task.get('prompt') or task.get('instructions') or task.get('input_text') or ''
    print(f"\n=== PROMPT / INSTRUCTIONS (Length: {len(prompt)}) ===")
    print(prompt[:1000])

    # Check custom_fields
    cf = task.get('custom_fields', {})
    print(f"\n=== CUSTOM FIELDS COUNT: {len(cf)} ===")
    
    # Check for repo or problem title
    for k, v in cf.items():
        if any(term in k.lower() for term in ['repo', 'instance', 'problem', 'issue', 'title', 'prompt', 'task']):
            if isinstance(v, (str, int, float, bool)) and len(str(v)) < 200:
                print(f"  {k}: {v}")

    # Check for comparative rationale or score
    for k, v in cf.items():
        if any(term in k.lower() for term in ['rationale', 'pref', 'score', 'final', 'verdict']):
            if isinstance(v, (str, int, float, bool)) and len(str(v)) < 300:
                print(f"  {k}: {v}")

    # Check trajectories / rollouts
    rollouts = task.get('rollouts') or task.get('trajectories') or []
    print(f"\n=== ROLLOUTS / TRAJECTORIES: {len(rollouts)} ===")
    if not rollouts:
        # Check inside custom_fields or task
        for k in ['model_a', 'model_b', 'rollout_a', 'rollout_b', 'trajectory_a', 'trajectory_b', 'side_a', 'side_b']:
            if k in task or k in cf:
                print(f"Found rollout key: {k}")

if __name__ == '__main__':
    inspect()
