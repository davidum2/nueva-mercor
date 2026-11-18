with open('task_74b080f5a1554daaba2595c070f210f7/page_full.html', 'r', encoding='utf-8') as f:
    html = f.read()

print('HTML size:', len(html))
keywords = ['testFileOutput_wrongType', 'missing_path', 'Dimension 7', 'Rubric 6', 'Rubric 9', 'smart i', 'Jeremy H']
for kw in keywords:
    count = html.count(kw)
    print(f"'{kw}' count in HTML: {count}")
