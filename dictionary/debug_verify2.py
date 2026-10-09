import json
import re
import sys
sys.path.insert(0, 'dictionary')
from build_vocab_json import generate_word_family, is_likely_real_word

data = json.load(open('dictionary/vocab_cards.json', 'r', encoding='utf-8'))
nodes = data['nodes']
vocab = set(n['label'] for n in nodes)

# Check if any of the missing words exist in the generated data
missing = ['unfold', 'unlikely', 'unknown', 'unfinished', 'predict', 'prefer', 'preview', 'rebuild', 'rewrite', 'redo']
for w in missing:
    found = any(n['label'] == w for n in nodes)
    print(f'{w}: {"EXISTS" if found else "MISSING"}')

print()
# Check which stem generates each word
for w in missing:
    for prefix in ['un', 'dis', 'pre', 'over', 'under', 'non', 'out', 're']:
        if w.startswith(prefix) and len(w) > len(prefix):
            stem = w[len(prefix):]
            if stem.isalpha():
                generated = generate_word_family(stem)
                if w in generated:
                    result = is_likely_real_word(w, vocab)
                    print(f'{w}: from "{stem}" -> generated={len(generated)} variants -> is_real={result}')
                    break
            else:
                print(f'{w}: invalid stem "{stem}"')
                break
    else:
        print(f'{w}: NOT GENERATED from any known prefix')
