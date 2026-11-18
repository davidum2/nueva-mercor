import json
import os
import sys

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_DIR = r'c:\desarrollo\nueva-mercor\task_task_f5ba2eb1464a4db2831f60a63283341d'

def inspect_details():
    with open(os.path.join(TASK_DIR, 'task_api.json'), 'r', encoding='utf-8') as f:
        task = json.load(f)

    print("=== REVIEW FEEDBACK ===")
    print(json.dumps(task.get('review_feedback'), indent=2))

    print("\n=== TASK LATEST EDGE & STATUS ===")
    print("Latest Edge ID:", task.get('task_latest_edge_id'))
    print("Latest Edge:", json.dumps(task.get('task_latest_edge'), indent=2))
    print("Status Defn:", json.dumps(task.get('task_status_defn'), indent=2))

    print("\n=== TASK PROMPT MESSAGES ===")
    for idx, msg in enumerate(task.get('task_prompt_messages', [])):
        print(f"Message #{idx+1}: role={msg.get('role')}")
        content = msg.get('content', '')
        print(content[:1500] if len(content) > 1500 else content)
        print("-" * 50)

    # Let's inspect custom_fields for problem statement, diffs, etc.
    cf = task.get('custom_fields', {})
    with open(os.path.join(TASK_DIR, 'all_custom_fields.json'), 'w', encoding='utf-8') as f:
        json.dump(cf, f, indent=2)

    print(f"\nWrote {len(cf)} custom_fields to all_custom_fields.json")

    # Look for diffs, trajectories, problem statement
    for k in sorted(cf.keys()):
        val = cf[k]
        if isinstance(val, str) and len(val) > 200:
            print(f"Long field: {k} (length={len(val)})")
        elif isinstance(val, (dict, list)):
            print(f"Complex field: {k} (type={type(val).__name__})")

    # Let's also inspect history_api.json
    with open(os.path.join(TASK_DIR, 'history_api.json'), 'r', encoding='utf-8') as f:
        hist = json.load(f)

    print(f"\n=== HISTORY ENTRIES ({len(hist)}) ===")
    for h in hist:
        ts = h.get('created_at')
        event = h.get('event') or h.get('action') or h.get('transition') or h.get('type')
        user = h.get('created_by_user_name') or h.get('created_by')
        edge = h.get('task_edge_id') or h.get('edge_name')
        notes = h.get('notes') or h.get('review_feedback')
        print(f"[{ts}] {event} by {user} (edge: {edge})")
        if notes:
            print(f"   Notes/Feedback: {notes}")

if __name__ == '__main__':
    inspect_details()
