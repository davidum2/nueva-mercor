with open('page_full.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('World Rubric')
print("Index of World Rubric:", idx)
sub = text[max(0, idx-2000):idx]
import re
headings = re.findall(r'<h[1-6][^>]*>(.*?)</h[1-6]>', sub)
print("Headings before World Rubric:", headings)
buttons = re.findall(r'<button[^>]*>(.*?)</button>', sub)
print("Buttons before World Rubric:", buttons[-5:])
