import json
from bs4 import BeautifulSoup

d = json.load(open('pharma_data.json', encoding='utf-8'))
soup = BeautifulSoup(open('debug/medipal.html', encoding='utf-8').read(), 'html.parser')

new_m = []
for icon in (soup.select_one('section#cFooter') or soup).select('.MstKpnErr'):
    row = icon.find_parent('div', class_='row') or icon.find_parent('tr') or icon.find_parent('div')
    
    name_el = row.select_one("td.MstHnm") or row.select_one("[id^='hnmy']")
    name = name_el.text.strip() if name_el else (row.text.strip().split("\n")[0] if row else "Unknown")
    
    if name == "Unknown" or not name:
        texts = [t.strip() for t in row.stripped_strings if t.strip()]
        if len(texts) > 3:
            name = texts[3]
            
    texts = [t.strip() for t in row.stripped_strings if t.strip()]
    
    code = ""
    maker = ""
    
    for t in texts:
        if t.isdigit() and len(t) >= 10:
            code = t
        elif any(m in t for m in ["製薬", "薬品", "工業", "ファーマ", "ラボ", "ケミカル", "キリン", "メディック", "興和", "ファルマ"]):
            maker = t
    
    if not maker and len(texts) > 1 and not texts[1].isdigit(): maker = texts[1]
    if not code and len(texts) > 2 and texts[2].isdigit(): code = texts[2]
    
    item = {
        "code": code,
        "maker": maker,
        "name": name,
        "remarks": "メーカー出荷調整品：入荷未定"
    }
    if item not in new_m:
        new_m.append(item)

d['medipal'] = new_m
json.dump(d, open('pharma_data.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f"Fixed {len(new_m)} Medipal items.")
