import re

with open('task_74b080f5a1554daaba2595c070f210f7/page_full.html', 'r', encoding='utf-8') as f:
    html = f.read()

# find URLs or endpoints
endpoints = set(re.findall(r'https?://[^\s"\'<>]+|/api/[^\s"\'<>]+', html))
for ep in sorted(endpoints):
    if any(k in ep for k in ['mercor', 'task', 'annotat', 'camp']):
        print(ep)
