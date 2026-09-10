import json, re
d = json.load(open('data/products.json', encoding='utf-8'))

def cats(name):
    n = name.lower()
    c = []
    if 'jacket' in n: c.append('jackets')
    if 'hood' in n and 'sweatshirt' not in n: c.append('hoodies')
    if 'sweatshirt' in n: c.append('sweatshirts')
    if 't shirt' in n or 't-shirt' in n: c.append('t-shirts')
    if 'collar' in n or 'polo' in n: c.append('polo')
    if 'print' in n: c.append('printed')
    return c or ['t-shirts']

def cardspec(p):
    """One short spec line for the card, from real data only."""
    by = {s['label'].lower(): s['value'] for s in p['specs']}
    bits = []
    mat = by.get('material')
    if isinstance(mat, str) and mat:
        bits.append(mat)
    gsm = by.get('gsm')
    if isinstance(gsm, list) and gsm:
        bits.append(' / '.join(gsm) + ' GSM')
    sizes = by.get('sizes available')
    if isinstance(sizes, list) and sizes:
        bits.append('Sizes ' + '-'.join(sizes))
    return ' · '.join(bits[:2])

for p in d:
    p['categories'] = cats(p['name'])
    p['cardspec'] = cardspec(p)

json.dump(d, open('data/products.json','w',encoding='utf-8'), indent=1, ensure_ascii=False)

from collections import Counter
c = Counter(x for p in d for x in p['categories'])
print(dict(c))
for p in d[:6]:
    print(f"  {p['name'][:50]:52} {p['categories']}  | {p['cardspec']}")
