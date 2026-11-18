import json

with open('autoqc_details.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

if isinstance(data, list):
    print("List of length", len(data), "type of [0]:", type(data[0]))
    if isinstance(data[0], str):
        print("First 5 elements:", data[:5])
elif isinstance(data, dict):
    print("Dict keys:", list(data.keys()))

    passed = item.get('passed')
    severity = item.get('severity')
    status = item.get('status')
    if passed is False or severity or status not in ['PASSED', 'PASS', True]:
        print(f"=== {title} (severity: {severity}, passed: {passed}, status: {status}) ===")
        print(json.dumps(item, indent=2))
