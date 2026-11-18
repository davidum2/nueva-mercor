import json

with open('task_api_dump.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

fields = data.get('task', {}).get('task_schema', {}).get('fields', [])
print(f"Total fields in schema: {len(fields)}")

rubric_fields = [f for f in fields if 'rubric' in f.get('field_id', '').lower() or 'rubric' in (f.get('label') or '').lower()]
print(f"Found {len(rubric_fields)} rubric fields:")

for f in rubric_fields:
    fid = f.get('field_id')
    lbl = f.get('label')
    ftype = f.get('field_type')
    opts = f.get('options')
    print(f" - ID: {fid:30s} | Type: {ftype:15s} | Label: {lbl}")
