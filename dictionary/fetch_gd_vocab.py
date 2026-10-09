import re
import json
from urllib import request

HTML = 'https://zy.gdedu.gov.cn/player/data1/transform/2022/2/12/11/32/c17c8dd89b3311eaa85a7efd8b80fdb8/2b66e3b683ee29971608647982213ebb.doc/html4/transform.html'

req = request.Request(HTML, headers={'User-Agent': 'Mozilla/5.0'})
resp = request.urlopen(req, timeout=30)
html = resp.read().decode('utf-8', errors='ignore')

# Extract all table rows with vocabulary data
pattern = r'<td[^>]*>(\d+)</td>\s*<td[^>]*>([^<]+)</td>\s*<td[^>]*>\[([^\]]+)\]</td>\s*<td[^>]*>([^<]+(?:<[^>]*>[^<]+)*?)</td>'
matches = re.findall(pattern, html)

words = []
seen = set()
for m in matches:
    num, word, phonetic, meaning = m
    w = word.strip()
    if w in seen or not w:
        continue
    seen.add(w)
    words.append({'word': w, 'phonetic': phonetic, 'meaning': meaning})

print(f'Guangdong vocab: {len(words)}')
with open(r'd:\project\math-visualization\dictionary\gd_1600.json', 'w', encoding='utf-8') as f:
    json.dump(words, f, ensure_ascii=False, indent=2)
print('Saved gd_1600.json')
