with open('task_74b080f5a1554daaba2595c070f210f7/page_raw_text.txt', 'r', encoding='utf-8') as f:
    text = f.read()

lines = text.splitlines()
for i, l in enumerate(lines):
    if 'AutoQC' in l:
        print(f'{i}: {l}')
