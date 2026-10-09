import re, os, glob

DICT_DIR = r'd:\project\math-visualization\dictionary'
NEW_VOCAB_FILE = os.path.join(DICT_DIR, '深圳中考英语词汇表.md')

# 1. 解析新词汇表
vocab = {}
with open(NEW_VOCAB_FILE, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line.startswith('|'):
            continue
        cells = [c.strip() for c in line.split('|')[1:-1]]
        if len(cells) >= 4:
            try:
                num = int(cells[0])
                word_raw = cells[1]
                phonetic = cells[2]
                meaning = cells[3]
                word = word_raw.split('(')[0].strip().lower()
                if word and word.isalpha():
                    vocab[word] = (phonetic, meaning)
            except ValueError:
                continue

print(f'新词汇表共 {len(vocab)} 条记录')

def clean_ph(raw):
    raw = raw.strip().strip('"').strip("'")
    if raw.startswith('[') and raw.endswith(']'):
        raw = raw[1:-1]
    return raw.strip()

def process_file(fp):
    with open(fp, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    i = 0
    updated = 0
    last_word = None

    while i < len(lines):
        line = lines[i]
        wm = re.match(r'^###\s+(\S+)', line)
        if wm:
            word = wm.group(1).lower()
            # 跳过重复的 ### 行
            if word == last_word:
                i += 1
                continue
            last_word = word

            # 收集块
            block = [line]
            i += 1
            while i < len(lines) and not lines[i].startswith('###'):
                block.append(lines[i])
                i += 1

            if word in vocab:
                new_phon, new_mean = vocab[word]
                new_phon = clean_ph(new_phon)
                cleaned = [line]
                for bl in block[1:]:
                    s = bl.strip()
                    if s.startswith('- **音标**'):
                        cleaned.append(f'- **音标**: [{new_phon}]')
                    elif s.startswith('- **释义**'):
                        cleaned.append(f'- **释义**: {new_mean}')
                    else:
                        cleaned.append(bl)
                new_lines.extend(cleaned)
                updated += 1
            else:
                cleaned = [line]
                for bl in block[1:]:
                    s = bl.strip()
                    if s.startswith('- **音标**'):
                        m = re.search(r'\[(.+?)\]', bl)
                        if m:
                            cleaned.append(f'- **音标**: [{clean_ph(m.group(1))}]')
                        else:
                            cleaned.append(bl)
                    else:
                        cleaned.append(bl)
                new_lines.extend(cleaned)
        else:
            new_lines.append(line)
            i += 1

    with open(fp, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    return updated

# 2. 分批处理
card_files = sorted(glob.glob(os.path.join(DICT_DIR, '联想记忆卡片_*.md')))

for fp in card_files:
    fname = os.path.basename(fp)
    updated = process_file(fp)
    print(f'  {fname}: 已更新 {updated} 条')

print('\n全部完成！')
