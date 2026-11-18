import json
import os
import sys

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

TASK_DIR = r'c:\desarrollo\nueva-mercor\task_task_f5ba2eb1464a4db2831f60a63283341d'

def inspect_eval():
    with open(os.path.join(TASK_DIR, 'all_custom_fields.json'), 'r', encoding='utf-8') as f:
        cf = json.load(f)

    # Let's inspect history entry #11 (which had the last submitted state before rejection)
    with open(os.path.join(TASK_DIR, 'history_api.json'), 'r', encoding='utf-8') as f:
        hdata = json.load(f)
    history = hdata['history']

    # Entry 9 was the last "Submit for Final QC" by Pravin K
    submit_entry = history[8] # 0-indexed: entry 9
    scf = submit_entry.get('custom_fields', {})

    print("=== LAST SUBMITTED RATINGS (From History Entry #9 by Pravin K) ===")
    print(f"Task Type: {scf.get('field_task_type')}")
    print(f"Rubric Count: {scf.get('field_rubric_count')}")
    print(f"Pairwise Preference: {scf.get('field_e511999a150a45c2b7145f808103d78c')}")
    print(f"Final Quality Score A: {scf.get('field_ta_final_quality_score_a')}")
    print(f"Final Quality Score B: {scf.get('field_ta_final_quality_score_b')}")
    print(f"\nComparative Rationale:\n{scf.get('field_1e32bd048d564685ba8ec51f9af11c70')}")

    print("\n=== DIMENSION SCORES & REASONS ===")
    for d in range(2, 10):
        print(f"\n--- Dimension {d} ---")
        sa = scf.get(f'field_ta_dim{d}_score_a')
        ra = scf.get(f'field_ta_dim{d}_reason_a')
        sb = scf.get(f'field_ta_dim{d}_score_b')
        rb = scf.get(f'field_ta_dim{d}_reason_b')
        print(f"Side A Score: {sa}")
        print(f"Side A Reason: {ra}")
        print(f"Side B Score: {sb}")
        print(f"Side B Reason: {rb}")

if __name__ == '__main__':
    inspect_eval()
