import re, json, html

TW = {
 'bg-black':'#000000','bg-white':'#ffffff','bg-gray-100':'#f3f4f6','bg-gray-200':'#e5e7eb',
 'bg-gray-300':'#d1d5db','bg-gray-400':'#9ca3af','bg-gray-500':'#6b7280','bg-gray-600':'#4b5563',
 'bg-gray-700':'#374151','bg-gray-800':'#1f2937','bg-gray-900':'#111827',
 'bg-red-300':'#fca5a5','bg-red-400':'#f87171','bg-red-500':'#ef4444','bg-red-600':'#dc2626','bg-red-700':'#b91c1c','bg-red-800':'#991b1b','bg-red-900':'#7f1d1d',
 'bg-orange-300':'#fdba74','bg-orange-400':'#fb923c','bg-orange-500':'#f97316','bg-orange-700':'#c2410c',
 'bg-yellow-200':'#fde68a','bg-yellow-300':'#fcd34d','bg-yellow-400':'#fbbf24','bg-yellow-500':'#f59e0b','bg-yellow-700':'#b45309',
 'bg-green-200':'#a7f3d0','bg-green-300':'#6ee7b7','bg-green-400':'#34d399','bg-green-500':'#10b981','bg-green-600':'#059669',
 'bg-green-700':'#047857','bg-green-800':'#065f46','bg-green-900':'#064e3b',
 'bg-teal-300':'#7dd3fc','bg-teal-400':'#2dd4bf','bg-teal-500':'#14b8a6','bg-teal-700':'#0f766e','bg-teal-900':'#134e4a',
 'bg-blue-200':'#bfdbfe','bg-blue-300':'#93c5fd','bg-blue-400':'#60a5fa','bg-blue-500':'#3b82f6',
 'bg-blue-600':'#2563eb','bg-blue-700':'#1d4ed8','bg-blue-800':'#1e40af','bg-blue-900':'#1e3a8a',
 'bg-indigo-300':'#a5b4fc','bg-indigo-400':'#818cf8','bg-indigo-500':'#6366f1','bg-indigo-700':'#4338ca','bg-indigo-900':'#312e81',
 'bg-purple-300':'#d8b4fe','bg-purple-400':'#c084fc','bg-purple-500':'#a855f7','bg-purple-700':'#7e22ce','bg-purple-900':'#581c87',
 'bg-pink-300':'#f9a8d4','bg-pink-400':'#f472b6','bg-pink-500':'#ec4899','bg-pink-700':'#be185d','bg-pink-900':'#831843',
}

def txt(s):
    return html.unescape(re.sub(r'<[^>]+>', '', s)).strip()

LABEL = re.compile(r'<span class="font-bold[^"]*">\s*([^<:]+?)\s*:?\s*</span>(.*?)(?=<span class="font-bold|<footer|</body>)', re.S)

out = []
for line in open('data/products.txt', encoding='utf-8'):
    slug, imgfile, title = line.strip().split('|')
    doc = open(f'data/raw/{slug}.html', encoding='utf-8').read()
    i = doc.find('<h2 class="text-2xl font-bold')
    body = doc[i:] if i > 0 else doc

    page_title = txt(re.search(r'<title>(.*?)</title>', doc, re.S).group(1))
    h2 = re.search(r'<h2 class="text-2xl font-bold[^"]*">(.*?)</h2>', doc, re.S)
    name = txt(h2.group(1)) if h2 else title

    specs, colors, desc = [], [], ''
    for label, blob in LABEL.findall(body):
        if label.lower().startswith('price'):
            continue
        if label.lower().startswith('product description'):
            paras = [txt(p) for p in re.findall(r'<p[^>]*>(.*?)</p>', blob, re.S)]
            desc = chr(10).join(p for p in paras if p and 'Lorem ipsum' not in p)
            continue
        btns = re.findall(r'<button([^>]*)>(.*?)</button>', blob, re.S)
        if label.lower() == 'color' or (btns and all(not txt(b[1]) for b in btns)):
            for attrs, _ in btns:
                for c in re.findall(r'(bg-(?:black|white|[a-z]+-\d{3}))', attrs):
                    if c in TW and TW[c] not in colors:
                        colors.append(TW[c])
            if colors and label.lower() != 'color':
                specs.append((label, None))  # placeholder, skip
            continue
        if btns:
            vals = [txt(b[1]) for b in btns if txt(b[1])]
            if vals:
                specs.append((label, vals))
            continue
        if label.lower().startswith('product description'):
            paras = [txt(p) for p in re.findall(r'<p[^>]*>(.*?)</p>', blob, re.S)]
            desc = '\n\n'.join(p for p in paras if p and 'Lorem ipsum' not in p)
            continue
        m = re.search(r'<span[^>]*>(.*?)</span>', blob, re.S)
        v = txt(m.group(1)) if m else txt(blob)
        if v:
            specs.append((label, v))

    specs = [(k, v) for k, v in specs if v]
    out.append({'slug': slug, 'name': name, 'title': page_title, 'image': f'{slug}.jpg',
                'specs': [{'label': k, 'value': v} for k, v in specs],
                'colors': colors, 'description': desc})

json.dump(out, open('data/products.json','w',encoding='utf-8'), indent=1, ensure_ascii=False)
print(len(out),'products')
for p in out:
    labels = [s['label'] for s in p['specs']]
    flag = '' if (p['description'] and labels) else '  <<< THIN'
    print(f"{p['slug'][:52]:54} {len(p['colors'])}c  {labels}{flag}")
