import json

with open('mercor_api_fetched.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

cur = data.get('task_current')
if cur:
    print("task_current keys:", list(cur.keys()))
    if 'rubric' in cur:
        print("rubric keys:", list(cur['rubric'].keys()) if isinstance(cur['rubric'], dict) else type(cur['rubric']))
    if 'evaluation' in cur:
        print("evaluation keys:", list(cur['evaluation'].keys()) if isinstance(cur['evaluation'], dict) else type(cur['evaluation']))
    if 'data' in cur:
        print("data keys:", list(cur['data'].keys()) if isinstance(cur['data'], dict) else type(cur['data']))
    if 'form' in cur:
        print("form keys:", list(cur['form'].keys()) if isinstance(cur['form'], dict) else type(cur['form']))
else:
    print("No task_current in mercor_api_fetched.json")
