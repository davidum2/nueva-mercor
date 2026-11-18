from bs4 import BeautifulSoup
import json

with open('page_full.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f, 'html.parser')

rows = soup.find_all('tr', class_=lambda c: c and 'group/row' in c)
print(f'Total rows in table: {len(rows)}')

rubrics = []
for i, row in enumerate(rows):
    cells = row.find_all('td')
    if len(cells) >= 5:
        num = cells[0].text.strip()
        rtype = cells[1].text.strip()
        criteria = cells[2].text.strip()
        dim = cells[3].text.strip()
        source = cells[4].text.strip()
        rubrics.append({
            'num': num,
            'type': rtype,
            'criteria': criteria,
            'dim': dim,
            'source': source
        })

for r in rubrics:
    print(f"{r['num']}: [{r['source']}] ({r['dim']}) -> {r['criteria']}")

with open('rubrics_table_parsed.json', 'w', encoding='utf-8') as f:
    json.dump(rubrics, f, indent=2)
