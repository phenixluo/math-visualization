import sys
sys.path.insert(0, r'd:\project\math-visualization\dictionary')
import build_vocab_json as bv

# 手动追踪generate_word_family('like')的执行过程
word = 'like'
word_lower = word.lower()
prefixes = ['un', 'dis', 'pre', 'over', 'under', 'non', 'out', 're']
suffixes = [('ing', ''), ('ed', ''), ('s', ''), ('ly', ''), ('er', ''), ('est', ''), ('tion', ''), ('ment', ''), ('ness', ''), ('ful', ''), ('less', '')]

variants = set()

# 后缀
for suffix, _ in suffixes:
    if word_lower.endswith(suffix) and len(word_lower) > len(suffix):
        stem = word_lower[:-len(suffix)]
        if len(stem) >= 2 and stem.isalpha():
            for sfx, _ in suffixes:
                if len(stem) + len(sfx) >= 2:
                    variant = stem + sfx
                    if variant != word_lower and variant.isalpha():
                        variants.add(variant)
    else:
        variant = word_lower + suffix
        if len(variant) >= 3 and variant.isalpha():
            variants.add(variant)

print(f"After suffix: {sorted(variants)}")

# 前缀
for prefix in prefixes:
    variant = prefix + word_lower
    if len(variant) >= 3 and variant.isalpha():
        variants.add(variant)

print(f"After prefix: {sorted(variants)}")

# 特殊规则：以e结尾
if word_lower.endswith('e') and len(word_lower) > 1:
    variant = word_lower[:-1] + 'ing'
    if len(variant) >= 3:
        variants.add(variant)
    variant = word_lower[:-1] + 'ed'
    if len(variant) >= 3:
        variants.add(variant)

print(f"After e-rule: {sorted(variants)}")

# 前缀+后缀组合
suffix_variants = {v for v in variants if v != word_lower and len(v) > len(word_lower)}
print(f"Suffix variants: {sorted(suffix_variants)}")
for sv in list(suffix_variants):
    for prefix in prefixes:
        candidate = prefix + sv
        if len(candidate) >= 3 and candidate.isalpha() and len(candidate) <= 15:
            variants.add(candidate)

print(f"After prefix+suffix combo: {sorted(variants)}")

# 过滤
variants = {v for v in variants if v != word_lower and len(v) >= 3}
variants = {v for v in variants if len(v) <= 15 and not any(c in v for c in ['xx', 'yy', 'zz'])}
print(f"Final variants: {sorted(variants)}")
print(f"unlikely in variants: {'unlikely' in variants}")
print(f"preview in variants: {'preview' in variants}")
print(f"unfold in variants: {'unfold' in variants}")
print(f"unfinished in variants: {'unfinished' in variants}")
