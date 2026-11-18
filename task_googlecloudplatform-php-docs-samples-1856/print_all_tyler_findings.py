import json

with open('task_googlecloudplatform-php-docs-samples-1856/tyler_audit_full.json', 'r', encoding='utf-8') as f:
    audit = json.load(f)

print(f"=== AUDIT {audit.get('qc_audit_id')} by {audit.get('created_by')} ===")
print("Created at:", audit.get('created_at'))
print("Verdict:", audit.get('verdict'))

sections = audit.get('outcome', {}).get('sections', [])
total_findings = 0
for s in sections:
    for d in s.get('dimensions', []):
        findings = d.get('findings', [])
        if findings or d.get('status') == 'fail':
            print(f"\n=======================================================")
            print(f"[{d.get('dim_id')}] {d.get('dimension')} --> STATUS: {d.get('status')}")
            for f in findings:
                total_findings += 1
                print(f"\n  * Finding: {f.get('title')} [{f.get('severity')}]")
                print(f"    Description: {f.get('description')}")
                if f.get('suggested_fix'):
                    print(f"    Suggested Fix: {f.get('suggested_fix')}")

print(f"\nTOTAL FINDINGS FLAGGED: {total_findings}")
