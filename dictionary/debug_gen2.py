"""详细调试词族生成"""
import sys
sys.path.insert(0, r'd:\project\math-visualization\dictionary')
from build_vocab_json import generate_word_family, is_likely_real_word

vocab = {'finish': ('', ''), 'like': ('', ''), 'know': ('', ''), 'view': ('', ''), 'fold': ('', '')}

for base in ['finish', 'like', 'know', 'view', 'fold']:
    families = generate_word_family(base)
    # 打印所有包含目标词的
    targets = ['unfinished', 'unlikely', 'unknown', 'unfold', 'predict', 'prefer', 'preview']
    for t in targets:
        if t in families:
            print(f"{base} -> {t}: passes={is_likely_real_word(t, vocab)}")
        elif t.startswith('un') or t.startswith('pre'):
            # 检查是否被过滤
            passed = is_likely_real_word(t, vocab)
            if not passed:
                print(f"{base} -> {t}: NOT in families, would_be_filtered={passed}")
