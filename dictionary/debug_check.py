"""检查preview/unfinished是否在vocab中"""
import json, os

DICT_DIR = r'd:\project\math-visualization\dictionary'
OUT_FILE = os.path.join(DICT_DIR, 'vocab_cards.json')

with open(OUT_FILE, encoding='utf-8') as f:
    data = json.load(f)

nodes = data.get('nodes', [])
words = {n['label'].lower(): n for n in nodes}

targets = ['unfold', 'unlikely', 'unknown', 'unfinished', 'predict', 'prefer', 'preview']
for t in targets:
    if t in words:
        n = words[t]
        print(f"{t}: type={n['type']}, id={n['id']}, meaning={n['meaning'][:30] if n['meaning'] else ''}")
    else:
        print(f"{t}: NOT FOUND")

# 检查review的词族边
if 'review' in words:
    rev_id = words['review']['id']
    edges = data.get('edges', [])
    for e in edges:
        if e.get('from') == rev_id:
            target = next((n['label'] for n in nodes if n['id'] == e.get('to')), '')
            if target in ['preview', 'reviewed', 'reviewing', 'reviews', 'reviewer']:
                print(f"review -> {target} (edge exists)")
