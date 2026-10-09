import sys
sys.path.insert(0, r'd:\project\math-visualization\dictionary')
from build_vocab_json import generate_word_family, is_likely_real_word, parse_vocab
import os

DICT_DIR = r'd:\project\math-visualization\dictionary'
VOCAB_FILE = os.path.join(DICT_DIR, '深圳中考英语词汇表.md')

with open(VOCAB_FILE, encoding='utf-8') as f:
    vocab = parse_vocab(f.read())

# 检查review和finish的词族
for base in ['review', 'finish', 'like', 'know']:
    if base in vocab:
        fams = generate_word_family(base)
        print(f"{base}: {len(fams)} variants")
        targets = ['preview', 'unfold', 'unlikely', 'unknown', 'unfinished', 'predict', 'prefer']
        for t in targets:
            if t in fams:
                print(f"  -> generates: {t}")
