import json
import os
import sys

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_DIR = r'c:\desarrollo\nueva-mercor\task_task_f5ba2eb1464a4db2831f60a63283341d'

def extract_all():
    with open(os.path.join(TASK_DIR, 'task_api.json'), 'r', encoding='utf-8') as f:
        task = json.load(f)

    cf = task.get('custom_fields', {})

    # 1. Prompt / Instructions
    prompt = cf.get('field_task_prompt', '')
    with open(os.path.join(TASK_DIR, 'prompt.md'), 'w', encoding='utf-8') as f:
        f.write(prompt)
    print(f"1. Prompt saved ({len(prompt)} chars)")

    # 2. Patches
    patch_a = cf.get('field_patch_a', '')
    with open(os.path.join(TASK_DIR, 'patch_a.diff'), 'w', encoding='utf-8') as f:
        f.write(patch_a)
    print(f"2. Patch A saved ({len(patch_a)} chars)")

    patch_b = cf.get('field_patch_b', '')
    with open(os.path.join(TASK_DIR, 'patch_b.diff'), 'w', encoding='utf-8') as f:
        f.write(patch_b)
    print(f"3. Patch B saved ({len(patch_b)} chars)")

    # 3. Model final answers
    fa_a = cf.get('field_final_answer_a', '')
    with open(os.path.join(TASK_DIR, 'final_answer_a.txt'), 'w', encoding='utf-8') as f:
        f.write(fa_a)
    fa_b = cf.get('field_final_answer_b', '')
    with open(os.path.join(TASK_DIR, 'final_answer_b.txt'), 'w', encoding='utf-8') as f:
        f.write(fa_b)
    print("4. Final answers A and B saved")

    # 4. Reviewer Feedback / Adjudication Rationale / Notes
    adj_rationale = cf.get('field_adj_rationale', '')
    notes = task.get('notes', '')
    review_feedback = task.get('review_feedback')
    with open(os.path.join(TASK_DIR, 'feedback_and_notes.txt'), 'w', encoding='utf-8') as f:
        f.write(f"=== REVIEW FEEDBACK ===\n{json.dumps(review_feedback, indent=2)}\n\n")
        f.write(f"=== NOTES ===\n{notes}\n\n")
        f.write(f"=== ADJ RATIONALE (FEEDBACK) ===\n{adj_rationale}\n")
    print("5. Feedback and notes saved")

    # 5. Ledger / Models
    ledger = cf.get('field_dl_run_ledger', '')
    with open(os.path.join(TASK_DIR, 'ledger.json'), 'w', encoding='utf-8') as f:
        f.write(ledger)
    print("6. Ledger saved")

    # 6. Verifiers
    with open(os.path.join(TASK_DIR, 'verifiers_api.json'), 'r', encoding='utf-8') as f:
        verifiers = json.load(f)
    print(f"7. Verifiers count: {len(verifiers)}")
    with open(os.path.join(TASK_DIR, 'verifiers_summary.txt'), 'w', encoding='utf-8') as f:
        for idx, v in enumerate(verifiers):
            crit = v.get('verifier_values', {}).get('criteria', '')
            f.write(f"[{idx+1}] ID: {v.get('verifier_id')}\n")
            f.write(f"    Criteria: {crit}\n")
            cf_vals = v.get('verifier_custom_field_values', {})
            f.write(f"    Ans A: {cf_vals.get('answer_a')} | Ans B: {cf_vals.get('answer_b')}\n")
            f.write(f"    Dim: {cf_vals.get('mapped_dimension')} | Src: {cf_vals.get('rubric_source')}\n")
            f.write(f"    Reason A: {cf_vals.get('reason_a')}\n")
            f.write(f"    Reason B: {cf_vals.get('reason_b')}\n\n")

    # 7. Check History list in history_api.json
    with open(os.path.join(TASK_DIR, 'history_api.json'), 'r', encoding='utf-8') as f:
        hist_data = json.load(f)

    # hist_data could be dict or list
    print(f"8. History data type: {type(hist_data).__name__}")
    if isinstance(hist_data, dict):
        print(f"   Keys: {list(hist_data.keys())}")
        # In mercor studio, history is often { "task_id": ..., "items": [...] } or a list of task revisions
        items = hist_data.get('items') or hist_data.get('history') or [hist_data]
    else:
        items = hist_data

    print(f"   History revisions count: {len(items)}")
    with open(os.path.join(TASK_DIR, 'history_summary.txt'), 'w', encoding='utf-8') as f:
        for i, item in enumerate(items):
            if isinstance(item, dict):
                f.write(f"--- REVISION #{i+1} ---\n")
                f.write(f"Updated at: {item.get('updated_at')} by {item.get('updated_by_user_name') or item.get('updated_by')}\n")
                f.write(f"Status: {item.get('task_status_defn', {}).get('status_name') if isinstance(item.get('task_status_defn'), dict) else item.get('task_status_id')}\n")
                f.write(f"Edge: {item.get('task_latest_edge', {}).get('transition_name') if isinstance(item.get('task_latest_edge'), dict) else item.get('task_latest_edge_id')}\n")
                item_cf = item.get('custom_fields', {})
                if item_cf.get('field_adj_rationale'):
                    f.write(f"Adj Rationale: {item_cf.get('field_adj_rationale')}\n")
                if item.get('notes'):
                    f.write(f"Notes: {item.get('notes')}\n")
                f.write("\n")

if __name__ == '__main__':
    extract_all()
