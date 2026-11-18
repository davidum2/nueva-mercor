import json

with open('task_googlecloudplatform-php-docs-samples-1856/tyler_audit_full.json', 'r', encoding='utf-8') as f:
    audit = json.load(f)

for s in audit.get('outcome', {}).get('sections', []):
    for d in s.get('dimensions', []):
        if d.get('dim_id') in ['rq_b1_binary_and_polarised', 'rq_b2_not_implementation_locked', 'rq_c1_reason_substance', 'rq_c2_score_reason_agreement']:
            print(f"[{d.get('dim_id')}] {d.get('dimension')}:")
            for f in d.get('findings', []):
                print(f"  * [{f.get('severity')}] {f.get('title')}: {f.get('description')}")
