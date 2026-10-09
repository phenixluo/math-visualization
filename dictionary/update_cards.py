import re, os, glob

DICT_DIR = r'd:\project\math-visualization\dictionary'
VOCAB_MD = os.path.join(DICT_DIR, '词汇表.md')

# 1. 从词汇表.md提取所有单词的音标和释义
vocab = {}
with open(VOCAB_MD, 'r', encoding='utf-8') as f:
    for line in f:
        m = re.match(r'- \*\*(\w+)\*\* \[([^\]]+)\]\s+(.+)', line.strip())
        if m:
            word = m.group(1).lower()
            phonetic = m.group(2).strip()
            meaning = m.group(3).strip()
            vocab[word] = (phonetic, meaning)

print(f'词汇表共 {len(vocab)} 条记录')

def clean_ph(p):
    return p.strip().strip('"').strip("'")

# 2. 处理每个联想记忆卡片文件
card_files = sorted(glob.glob(os.path.join(DICT_DIR, '联想记忆卡片_*.md')))

for fp in card_files:
    fname = os.path.basename(fp)
    with open(fp, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    new_lines = []
    i = 0
    updated_count = 0

    while i < len(lines):
        line = lines[i]
        # 检测 ### word 行
        wm = re.match(r'^###\s+(\S+)', line)
        if wm:
            word = wm.group(1).lower()
            block_lines = [line]
            i += 1
            # 收集整个块
            while i < len(lines) and not lines[i].startswith('###'):
                block_lines.append(lines[i])
                i += 1

            # 找音标行和释义行
            phon_idx = -1
            mean_idx = -1
            for j, bl in enumerate(block_lines):
                if bl.strip().startswith('- **音标**'):
                    phon_idx = j
                elif bl.strip().startswith('- **释义**'):
                    mean_idx = j

            # 重建块
            cleaned = []
            for j, bl in enumerate(block_lines):
                if j == phon_idx:
                    # 提取音标内容
                    raw = bl
                    # 去掉前缀
                    rest = raw.split('音标**:')[-1].strip()
                    # 去掉引号
                    rest = rest.strip('"').strip("'")
                    # 去掉多余的 [
                    if rest.startswith('[['):
                        rest = rest[1:]  # 变成 [xxx]
                    # 确保有完整括号
                    if rest.startswith('[') and not rest.endswith(']'):
                        rest = rest + ']'
                    # 提取内部
                    bm = re.search(r'\[(.+?)\]', rest)
                    if bm:
                        inner = clean_ph(bm.group(1))
                    else:
                        inner = clean_ph(rest.strip('[]'))

                    if word in vocab:
                        phon, mean = vocab[word]
                        phon = clean_ph(phon)
                        cleaned.append(f'- **音标**: [{phon}]')
                        cleaned.append(f'- **释义**: {mean}')
                        updated_count += 1
                    else:
                        cleaned.append(f'- **音标**: [{inner}]')
                        cleaned.append(block_lines[mean_idx] if mean_idx >= 0 else '')
                elif j == mean_idx and phon_idx >= 0 and word in vocab:
                    # 跳过原释义行，已被替换
                    pass
                else:
                    cleaned.append(bl)

            new_lines.extend(cleaned)
        else:
            new_lines.append(line)
            i += 1

    new_content = '\n'.join(new_lines)
    with open(fp, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f'  {fname}: 已校准 {updated_count} 条')

# 3. 检查残留
remaining = 0
for fp in card_files:
    with open(fp, 'r', encoding='utf-8') as f:
        c = f.read()
    remaining += len(re.findall(r'\[\[', c))

print(f'\n残留双括号: {remaining}')
print('全部完成！')
