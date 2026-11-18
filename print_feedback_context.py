with open('task_74b080f5a1554daaba2595c070f210f7/reviewer_feedback_tab.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'Feedback for writer' in l:
        print(f"=== Line {i} ===")
        for j in range(max(0, i-5), min(len(lines), i+30)):
            print(f"{j}: {lines[j].strip()}")
