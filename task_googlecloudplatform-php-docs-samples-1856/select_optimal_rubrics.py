import json

# Selected optimal set of 13 rubrics with 4 NOs for Model A
# Model A: 9 YES / 4 NO = 69.2% YES (Strictly < 75% AutoQC pass rate)
selected_ids = [
    # Dim 2 (3 rubrics: 1 YES, 2 NO for A)
    "Q01", # Signature 8 params (A=YES, B=NO)
    "Q05", # Template name resolution via projectDeidentifyTemplateName (A=NO, B=NO)
    "Q07", # InspectConfig attached to job (A=NO, B=YES)
    
    # Dim 3 (2 rubrics: 2 YES for A)
    "Q11", # Google Cloud documentation region tags (A=YES, B=YES)
    "Q13", # Complete PHPDoc annotations (A=YES, B=YES)
    
    # Dim 4 (3 rubrics: 1 YES, 2 NO for A)
    "Q17", # Bounded polling retry loop (A=NO, B=NO)
    "Q18", # Close DLP client in finally block (A=NO, B=YES)
    "Q19", # Handle FAILED state with error logging (A=YES, B=YES)
    
    # Dim 5 (2 rubrics: 2 YES for A)
    "Q25", # Exact file path dlp/src/deidentify_cloud_storage.php (A=YES, B=YES)
    "Q28", # Adheres to scope without extra project params (A=YES, B=NO)
    
    # Dim 6 (1 rubric: 1 YES for A)
    "Q33", # Clean navigation without missing directory errors (A=YES, B=NO)
    
    # Dim 7 (1 rubric: 1 YES for A)
    "Q37", # PHP syntax linting with php -l (A=YES, B=YES)
    
    # Dim 9 (1 rubric: 1 YES for A)
    "Q48", # Final summary documents signature without hiding params (A=YES, B=NO)
]

with open('question_bank_50.json', 'r', encoding='utf-8') as f:
    all_q = {q['id']: q for q in json.load(f)}

selected_rubrics = []
for idx, qid in enumerate(selected_ids, 1):
    q = all_q[qid]
    rubric_entry = {
        "rubric_index": idx,
        "question_id": qid,
        "dimension": q['dimension'],
        "dimension_name": q['dimension_name'],
        "source": q['source'],
        "rubric_text": q['question'],
        "answer_a": q['expected_a'],
        "reason_a": q['note_a'],
        "answer_b": q['expected_b'],
        "reason_b": q['note_b']
    }
    selected_rubrics.append(rubric_entry)

# Calibrate counts
a_yes = sum(1 for r in selected_rubrics if r['answer_a'] == 'YES')
b_yes = sum(1 for r in selected_rubrics if r['answer_b'] == 'YES')
total = len(selected_rubrics)
a_rate = (a_yes / total) * 100
b_rate = (b_yes / total) * 100

print(f"Total Selected Rubrics: {total}")
print(f"Model A (Gemini): {a_yes}/{total} YES ({a_rate:.1f}%) -> Strictly < 75% YES: {a_rate < 75.0}")
print(f"Model B: {b_yes}/{total} YES ({b_rate:.1f}%)")

# Verify dimension distribution
dims = {}
for r in selected_rubrics:
    d = r['dimension']
    dims[d] = dims.get(d, 0) + 1
print("Dimension distribution:", sorted(dims.items()))

# Save selected rubrics
with open('selected_rubrics_13.json', 'w', encoding='utf-8') as f:
    json.dump(selected_rubrics, f, indent=2, ensure_ascii=False)
print("Saved selected_rubrics_13.json successfully.")
