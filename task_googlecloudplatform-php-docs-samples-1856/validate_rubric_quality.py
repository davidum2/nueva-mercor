import json
import re

with open('selected_rubrics_13.json', 'r', encoding='utf-8') as f:
    rubrics = json.load(f)

print(f"Validating {len(rubrics)} selected rubrics...\n")

issues = []
for r in rubrics:
    idx = r['rubric_index']
    qid = r['question_id']
    text = r['rubric_text']
    ans_a = r['answer_a']
    reason_a = r['reason_a']
    ans_b = r['answer_b']
    reason_b = r['reason_b']
    
    words_a = len(reason_a.split())
    words_b = len(reason_b.split())
    
    # Check word counts
    if words_a < 15:
        issues.append(f"Rubric {idx} ({qid}) Side A has only {words_a} words (< 15)")
    if words_b < 15:
        issues.append(f"Rubric {idx} ({qid}) Side B has only {words_b} words (< 15)")
        
    # Check citations
    has_cite_a = any(c in reason_a for c in ['patch_a.diff', 'Step ', 'dlp/', 'L', 'line'])
    has_cite_b = any(c in reason_b for c in ['patch_b.diff', 'Step ', 'dlp/', 'L', 'line'])
    if not has_cite_a:
        issues.append(f"Rubric {idx} ({qid}) Side A missing concrete citation")
    if not has_cite_b:
        issues.append(f"Rubric {idx} ({qid}) Side B missing concrete citation")

print(f"Total issues found: {len(issues)}")
for issue in issues:
    print(" - ", issue)

if not issues:
    print("ALL RUBRICS PASS VALIDATION! 100% compliant with word counts and citations.")
