import json

# Inspect the task history dump we got earlier
with open('task_googlecloudplatform-php-docs-samples-1856/tyler_audit_full.json', 'r', encoding='utf-8') as f:
    audit = json.load(f)

print("Subject ID:", audit.get('subject_id'))
print("Subject version:", audit.get('subject_version'))

# Now let's see what custom fields were captured in the audit
sub = audit.get('subject_snapshot') or audit.get('snapshot') or audit.get('subject') or {}
print("Snapshot keys:", list(sub.keys()) if isinstance(sub, dict) else type(sub))
if isinstance(sub, dict) and 'custom_fields' in sub:
    cf = sub['custom_fields']
    r_keys = [k for k in cf if 'rubric' in k]
    print(f"Total rubric keys in snapshot: {len(r_keys)}")
    for k in sorted(r_keys):
        if '10' in k or '11' in k or '12' in k or '13' in k or '14' in k:
            print(f"  {k} = {repr(cf[k])}")
