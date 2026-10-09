import re, os, sys, glob

DICT_DIR = r'd:\project\math-visualization\dictionary'
VOCAB_FILE = os.path.join(DICT_DIR, '深圳中考英语词汇表.md')

ALIASES = {
    'behavior': 'behaviour',
    'color': 'colour',
    'favorite': 'favourite',
    'favor': 'favour',
    'labor': 'labour',
    'neighbor': 'neighbour',
    'humor': 'humour',
    'center': 'centre',
    'meter': 'metre',
    'gray': 'grey',
    'jewelry': 'jewellery',
    'traveling': 'travelling',
    'traveled': 'travelled',
    'organize': 'organise',
    'realize': 'realise',
    'apologize': 'apologise',
}

LOST_MNEMONICS = {
    'able': '"Be able to do something" - 能够做某事',
    'ache': '"My head aches" - 我头疼',
    'active': '"Take an active part in" - 积极参与',
    'advice': '"A piece of advice" - 一条建议',
    'afraid': '"Don\'t be afraid" - 别害怕',
    'agree': '"I agree with you" - 我同意你的看法',
    'birth': '"Give birth to a baby" - 生孩子',
    'black': '"Black and white" - 黑白分明',
    'break': '"Take a break" - 休息一下',
    'build': '"Build a bridge" - 建一座桥',
}


def load_vocab():
    vocab = {}
    with open(VOCAB_FILE, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line.startswith('|'):
                continue
            cells = [c.strip() for c in line.split('|')[1:-1]]
            if len(cells) < 4:
                continue
            try:
                int(cells[0])
            except ValueError:
                continue
            word = cells[1].split('(')[0].strip().lower()
            if not word or not word.isalpha():
                continue
            phon = cells[2].strip().strip('"').strip("'")
            while len(phon) >= 2 and phon.startswith('[') and phon.endswith(']'):
                phon = phon[1:-1].strip()
            vocab[word] = (phon, cells[3])
    return vocab


def lookup(word, vocab):
    w = word.lower()
    if w in vocab:
        return w
    for a, v in ALIASES.items():
        if w.startswith(a):
            cand = v + w[len(a):]
            if cand in vocab:
                return cand
    return None


def process_file(fp, vocab):
    with open(fp, encoding='utf-8') as f:
        lines = f.read().split('\n')

    # ---- 阶段1：清理旧的展开内容（保证幂等） ----
    cleaned = []
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if line.startswith('- **词族联想**') and '未在词汇表中' in line:
            i += 1
            continue
        if line.startswith('#### '):
            i += 1
            while i < len(lines) and not (lines[i].startswith('### ')
                                         or lines[i].startswith('---')
                                         or lines[i].startswith('## ')):
                if lines[i].startswith('- **记忆口诀**'):
                    cleaned.append(lines[i].rstrip())
                i += 1
            continue
        cleaned.append(line)
        i += 1
    lines = cleaned

    # ---- 阶段2：逐块重建并展开词族 ----
    out = []
    i = 0
    st = {'blocks': 0, 'expanded': 0, 'fix_def': 0, 'fix_mn': 0}
    unmatched = []
    while i < len(lines):
        line = lines[i]
        if line.startswith('### '):
            word = line[4:].strip().lower()
            block = [line]
            i += 1
            while i < len(lines) and not (lines[i].startswith('### ')
                                         or lines[i].startswith('## ')
                                         or lines[i].startswith('---')):
                block.append(lines[i].rstrip())
                i += 1
            st['blocks'] += 1

            phon_line = None
            def_line = None
            fam_line = None
            mn_line = None
            others = []
            for bl in block[1:]:
                s = bl.strip()
                if not s:
                    continue
                if s.startswith('- **音标**') and phon_line is None:
                    phon_line = s
                elif s.startswith('- **释义**') and def_line is None:
                    def_line = s
                elif s.startswith('- **词族联想**') and fam_line is None:
                    fam_line = s
                elif s.startswith('- **记忆口诀**') and mn_line is None:
                    mn_line = s
                else:
                    others.append(s)

            nb = [line]
            if phon_line:
                nb.append(phon_line)
            if def_line:
                nb.append(def_line)
            else:
                vw = lookup(word, vocab)
                if vw:
                    nb.append(f'- **释义**: {vocab[vw][1]}')
                    st['fix_def'] += 1
            if fam_line:
                nb.append(fam_line)
                if not mn_line and word in LOST_MNEMONICS:
                    mn_line = f'- **记忆口诀**: {LOST_MNEMONICS[word]}'
                    st['fix_mn'] += 1
            if mn_line:
                nb.append(mn_line)
            nb.extend(others)

            if fam_line:
                fam_text = fam_line.split(':', 1)[1] if ':' in fam_line else ''
                words_list = [w.strip() for w in fam_text.split(',') if w.strip()]
                subs = []
                seen = set()
                um = []
                for w in words_list:
                    c = re.sub(r'[^a-zA-Z]', '', w).lower()
                    if not c or c == word or c in seen:
                        continue
                    vw = lookup(c, vocab)
                    if vw:
                        seen.add(c)
                        ph, mean = vocab[vw]
                        subs += [f'#### {w}', f'- **音标**: [{ph}]', f'- **释义**: {mean}', '']
                    else:
                        um.append(w)
                if subs:
                    nb.append('')
                    nb.extend(subs)
                    st['expanded'] += len(seen)
                if um:
                    unmatched.append((word, um))

            while nb and nb[-1] == '':
                nb.pop()
            nb.append('')
            out.extend(nb)
        else:
            out.append(line)
            i += 1

    with open(fp, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(out))
    return st, unmatched


def main():
    vocab = load_vocab()
    print(f'词汇表加载: {len(vocab)} 条')
    args = sys.argv[1:]
    if args:
        files = [a if os.path.isabs(a) else os.path.join(DICT_DIR, a) for a in args]
    else:
        files = sorted(glob.glob(os.path.join(DICT_DIR, '联想记忆卡片_*.md')))
    for fp in files:
        st, um = process_file(fp, vocab)
        print(f"\n== {os.path.basename(fp)} ==")
        print(f"  块 {st['blocks']} | 词族展开 {st['expanded']} | 补释义 {st['fix_def']} | 补口诀 {st['fix_mn']}")
        for w, ul in um:
            print(f"  · {w}: {', '.join(ul)}")


if __name__ == '__main__':
    main()
