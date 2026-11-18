with open('task_74b080f5a1554daaba2595c070f210f7/page_raw_text.txt', 'r', encoding='utf-8') as f:
    text = f.read()

lines = text.splitlines()
for i, l in enumerate(lines):
    if 'Deliverable AutoQC' in l:
        print(f'=== AutoQC at line {i} ===')
        for j in range(i, min(len(lines), i+80)):
            print(f'{j}: {lines[j].strip()}')
