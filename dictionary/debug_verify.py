import json
import sys
sys.path.insert(0, 'dictionary')
from build_vocab_json import is_likely_real_word

data = json.load(open('dictionary/vocab_cards.json', 'r', encoding='utf-8'))
nodes = data['nodes']
vocab = set(n['label'] for n in nodes)

# Check if key stems are in vocab
for stem in ['fold', 'like', 'known', 'finish', 'dict', 'build', 'write', 'do', 'act', 'turn', 'live', 'line', 'view']:
    print(f'{stem}: {"IN VOCAB" if stem in vocab else "NOT IN VOCAB"}')

print()
# Test is_likely_real_word for missing words
for w in ['unfold', 'unlikely', 'unknown', 'unfinished', 'predict', 'prefer', 'preview', 'rebuild', 'rewrite', 'redo', 'react', 'outlive', 'outline']:
    result = is_likely_real_word(w, vocab)
    print(f'{w}: {"PASS" if result else "FAIL"}')
