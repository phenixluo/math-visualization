import json
import sys
sys.path.insert(0, 'dictionary')
from build_vocab_json import generate_word_family, is_likely_real_word

data = json.load(open('dictionary/vocab_cards.json', 'r', encoding='utf-8'))
nodes = data['nodes']
vocab = set(n['label'] for n in nodes)

# Check which stems generate the missing words
stems_to_check = ['fold', 'likely', 'known', 'finished', 'dict', 'fer', 'view']
for stem in stems_to_check:
    if stem in vocab:
        generated = generate_word_family(stem)
        print(f'{stem} (IN VOCAB): generates {len(generated)} variants')
        for w in ['unfold', 'unlikely', 'unknown', 'unfinished', 'predict', 'prefer', 'preview']:
            if w in generated:
                result = is_likely_real_word(w, vocab)
                print(f'  {w}: {"PASS" if result else "FAIL"}')
    else:
        print(f'{stem}: NOT IN VOCAB')

# Check how many family words "finished" has
print()
for n in nodes:
    if n['label'] == 'finished':
        print(f'finished node found: id={n["id"]}, type={n["type"]}')
        break
