import json

with open('task_74b080f5a1554daaba2595c070f210f7/textareas_full.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for item in data:
    if item['valueLength'] > 0:
        print(f"=== Textarea {item['index']} ({item['label']}) ===")
        print(item['value'])
        print("="*60)
