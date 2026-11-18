with open('task_74b080f5a1554daaba2595c070f210f7/reviewer_feedback_tab.txt', 'r', encoding='utf-8') as f:
    text = f.read()

import re
# Look for sections like "Comment", "Feedback", "Note", "Review"
matches = re.findall(r'(?:comment|feedback|rejection|note|adjudication).*', text, re.IGNORECASE)
for m in matches[:15]:
    print(m)
