import json

with open(r'C:\Users\david\.gemini\antigravity-ide\brain\455c0c0f-ea7d-48eb-8582-458ac3b8551f\.system_generated\logs\transcript.jsonl', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for line in lines[-40:]:
    data = json.loads(line)
    t = data.get('type')
    if t in ('USER_INPUT', 'PLANNER_RESPONSE'):
        content = data.get('content', '')
        # print first few lines of content
        lines_c = content.split('\n')
        preview = '\n'.join(lines_c[:10])
        print(f"=== Step {data.get('step_index')} ({t}) ===")
        print(preview)
        print("...\n")
