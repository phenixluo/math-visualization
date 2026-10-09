"""调试：检查review的词族和preview的过滤"""
import sys
sys.path.insert(0, r'd:\project\math-visualization\dictionary')
from build_vocab_json import generate_word_family, is_likely_real_word, parse_vocab
import os

DICT_DIR = r'd:\project\math-visualization\dictionary'
VOCAB_FILE = os.path.join(DICT_DIR, '深圳中考英语词汇表.md')

with open(VOCAB_FILE, encoding='utf-8') as f:
    vocab = parse_vocab(f.read())

print(f"vocab大小: {len(vocab)}")
print(f"'review' in vocab: {'review' in vocab}")
print(f"'finish' in vocab: {'finish' in vocab}")

# review的词族
families = generate_word_family('review')
print(f"\n=== review的词族 ===")
print(families)

# preview通过过滤吗？
print(f"\npreview passes filter: {is_likely_real_word('preview', vocab)}")
print(f"unfold passes filter: {is_likely_real_word('unfold', vocab)}")
print(f"unlikely passes filter: {is_likely_real_word('unlikely', vocab)}")
print(f"unknown passes filter: {is_likely_real_word('unknown', vocab)}")
print(f"unfinished passes filter: {is_likely_real_word('unfinished', vocab)}")
print(f"predict passes filter: {is_likely_real_word('predict', vocab)}")
print(f"prefer passes filter: {is_likely_real_word('prefer', vocab)}")

# 检查哪个词能生成这些
targets = ['unfold', 'unlikely', 'unknown', 'unfinished', 'predict', 'prefer', 'preview']
for target in targets:
    for word in vocab:
        fams = generate_word_family(word)
        if target in fams:
            print(f"{target} generated from '{word}'")
            break
    else:
        print(f"{target}: NOT generated from any vocab word")
