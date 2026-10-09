"""详细调试：检查每个缺失词的产生过程"""
import sys
sys.path.insert(0, r'd:\project\math-visualization\dictionary')
from build_vocab_json import generate_word_family, is_likely_real_word, parse_vocab
import os

DICT_DIR = r'd:\project\math-visualization\dictionary'
VOCAB_FILE = os.path.join(DICT_DIR, '深圳中考英语词汇表.md')

with open(VOCAB_FILE, encoding='utf-8') as f:
    vocab = parse_vocab(f.read())

print(f"词汇表共 {len(vocab)} 词")
print()

# 检查各词的生成过程
missing_words = ['unfold', 'unlikely', 'unknown', 'unfinished', 'predict', 'prefer', 'preview']

for w in missing_words:
    # 找到可能生成该词的词根
    for prefix in ['un', 'dis', 'pre', 'over', 'under', 'non', 'out', 're']:
        if w.startswith(prefix):
            stem = w[len(prefix):]
            in_vocab = stem in vocab
            passes = is_likely_real_word(w, vocab)
            print(f"{w}: prefix='{prefix}', stem='{stem}', in_vocab={in_vocab}, passes_filter={passes}")
            # 检查哪个主词能生成它
            for main_word in vocab:
                families = generate_word_family(main_word)
                if w in families:
                    print(f"  -> generated from '{main_word}'")
            break

print("\n=== finish 的词族 ===")
families = generate_word_family('finish')
print(families)
print(f"unfinished in families: {'unfinished' in families}")
print(f"unfinish in families: {'unfinish' in families}")
