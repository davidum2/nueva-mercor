import json
import os
import sys

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_DIR = r'c:\desarrollo\nueva-mercor\task_task_f5ba2eb1464a4db2831f60a63283341d'

def dump_full_history():
    with open(os.path.join(TASK_DIR, 'history_api.json'), 'r', encoding='utf-8') as f:
        data = json.load(f)
    history = data['history']

    print(f"Total history entries: {len(history)}")
    for i, h in enumerate(history):
        user = h.get('created_by_user_name') or h.get('created_by')
        status = h.get('task_status_defn', {}).get('status_name') if isinstance(h.get('task_status_defn'), dict) else h.get('task_status_id')
        edge = h.get('task_latest_edge', {}).get('transition_name') if isinstance(h.get('task_latest_edge'), dict) else h.get('task_latest_edge_id')
        ts = h.get('created_at')
        notes = h.get('notes')
        rf = h.get('review_feedback')
        cf = h.get('custom_fields', {})

        print(f"\n================ ENTRY #{i+1} ================")
        print(f"User: {user} | Status: {status} | Edge: {edge} | Created: {ts}")
        if notes:
            print(f"Notes: {notes}")
        if rf:
            print(f"Review Feedback: {json.dumps(rf, indent=2)}")
        
        # Check specific custom fields
        for field in ['field_adj_rationale', 'field_1e32bd048d564685ba8ec51f9af11c70', 'field_ta_dim6_score_a', 'field_ta_dim6_reason_a', 'field_rubric_count']:
            if cf.get(field):
                val = str(cf.get(field))
                if len(val) > 200:
                    val = val[:200] + '...'
                print(f"  {field}: {val}")

if __name__ == '__main__':
    dump_full_history()
