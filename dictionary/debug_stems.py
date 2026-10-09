import json
data = json.load(open('dictionary/vocab_cards.json', 'r', encoding='utf-8'))
nodes = data['nodes']
vocab = set(n['label'] for n in nodes)
stems = ['fold', 'likely', 'known', 'finished', 'dict', 'fer', 'view']
for s in stems:
    status = "IN VOCAB" if s in vocab else "NOT IN VOCAB"
    print(f'{s}: {status}')
print()
for w in ['unfold', 'unlikely', 'unknown', 'unfinished', 'predict', 'prefer', 'preview']:
    found = any(n['label'] == w for n in nodes)
    print(f'{w}: {"EXISTS" if found else "MISSING"}')
