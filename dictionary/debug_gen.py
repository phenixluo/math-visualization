"""调试：检查like/fold/finish的词族生成"""
import sys
sys.path.insert(0, r'd:\project\math-visualization\dictionary')
from build_vocab_json import generate_word_family, is_likely_real_word

# 模拟vocab（只有部分词）
vocab = {'finish': ('', ''), 'like': ('', ''), 'know': ('', ''), 'view': ('', ''), 'fold': ('', '')}

for base in ['finish', 'like', 'know', 'view', 'fold']:
    families = generate_word_family(base)
    print(f"\n=== {base} 的词族 ===")
    print(families)
    # 检查缺失词是否在其中
    for w in ['unfinished', 'unlikely', 'unknown', 'unfold', 'preview']:
        if w in families:
            passes = is_likely_real_word(w, vocab)
            print(f"  {w}: generated={w in families}, passes_filter={passes}")
