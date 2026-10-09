"""
将深圳中考全量词汇表 + 联想记忆卡片合并成结构化字典 JSON。
- 主节点：深圳中考词汇表全部词条（约1579个）
- 词族边：来自联想卡片的词族联想关系
- 规则驱动：增删词条只需更新 markdown 文件，重新跑此脚本即可
"""
import re, os, json, time, urllib.request
from collections import Counter

DICT_DIR = r'd:\project\math-visualization\dictionary'
VOCAB_FILE = os.path.join(DICT_DIR, '深圳中考英语词汇表.md')
CARD_FILES = [
    ('A-B', '联想记忆卡片_A-B.md'),
    ('C',   '联想记忆卡片_C.md'),
    ('D-M', '联想记忆卡片_D-M.md'),
    ('N-R', '联想记忆卡片_N-R.md'),
    ('S',   '联想记忆卡片_S.md'),
    ('T',   '联想记忆卡片_T.md'),
    ('U',   '联想记忆卡片_U.md'),
    ('V',   '联想记忆卡片_V.md'),
    ('W',   '联想记忆卡片_W.md'),
    ('Y',   '联想记忆卡片_Y.md'),
    ('Z',   '联想记忆卡片_Z.md'),
]
OUT_FILE = os.path.join(DICT_DIR, 'vocab_cards.json')

BATCH_COLORS = {
    'A-B': '#fbbf24', 'C': '#60a5fa', 'D-M': '#a78bfa',
    'N-R': '#34d399', 'S': '#f87171', 'T': '#f472b6',
    'U': '#fbbf24',   'V': '#60a5fa', 'W': '#a78bfa',
    'Y': '#34d399',   'Z': '#f87171',
}

ALIASES = {
    'behaviour': 'behavior', 'colour': 'color', 'favour': 'favor',
    'labour': 'labor', 'neighbour': 'neighbor', 'organisation': 'organization',
    'recognise': 'recognize', ' travelling': 'traveling', 'defence': 'defense',
    'licence': 'license', 'practise': 'practice', 'realise': 'realize',
    'optimise': 'optimize', 'centre': 'center', 'metre': 'meter',
    'theatre': 'theater', 'catalogue': 'catalog', 'encyclopaedia': 'encyclopedia',
}


def _is_valid_stem(word):
    """判断词根是否适合做派生词生成（拒绝时间名词、代词、反身代词、介词、副词等）"""
    w = word.lower()
    # 反身代词词根
    self_stems = {'myself', 'yourself', 'himself', 'herself', 'itself',
                  'ourselves', 'yourselves', 'themselves'}
    if w in self_stems or any(w.startswith(ss) for ss in self_stems):
        return False
    # 代词词根
    pron_stems = {'i', 'me', 'my', 'you', 'your', 'he', 'him', 'his',
                  'she', 'her', 'it', 'its', 'we', 'us', 'our', 'they',
                  'them', 'their', 'who', 'whom', 'whose', 'what', 'which',
                  'that', 'this', 'these', 'those', 'one', 'ones'}
    if w in pron_stems:
        return False
    # 时间名词词根（Monday/Tuesday/weekend/yesterday 等不可加任何前缀后缀）
    time_noun_stems = {
        'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
        'yesterday', 'today', 'tomorrow', 'tonight', 'weekend', 'weekday',
        'daybeforeyesterday', 'midweek', 'week',
    }
    if w in time_noun_stems:
        return False
    # 含时间名词后缀的复合词（如 -day 结尾的时间词）
    if w.endswith('day') and w not in {'birthday', 'holiday', 'daydream', 'daybed', 'daylong', 'daytime'}:
        return False
    # 常见介词/副词词根（about/around/above/after 等不可加前缀）
    prep_adv_stems = {
        'about', 'above', 'across', 'after', 'against', 'along', 'among', 'around',
        'at', 'away', 'back', 'before', 'behind', 'below', 'beneath', 'beside',
        'between', 'beyond', 'by', 'down', 'during', 'for', 'from', 'here',
        'in', 'inside', 'into', 'near', 'now', 'of', 'off', 'on', 'onto',
        'out', 'outside', 'over', 'past', 'since', 'through', 'throughout',
        'toward', 'towards', 'under', 'up', 'upon', 'with', 'within', 'without',
        'yet', 'well', 'very', 'too', 'always', 'often', 'ever', 'never',
        'just', 'only', 'even', 'also', 'then', 'there', 'where', 'when',
        'how',
    }
    if w in prep_adv_stems:
        return False
    return True


def find_vocab_family(word, vocab):
    """在词汇表中查找与 word 同词族的词（只返回词汇表中已存在的真实单词）"""
    if not word or len(word) < 3:
        return []
    word_lower = word.lower()
    related = set()

    # 常见后缀
    suffixes = ['ing', 'ed', 'ly', 'er', 'est', 'tion', 'sion', 'ment',
                'ness', 'ful', 'less', 'able', 'ible', 'al', 'ity', 'ty',
                'ous', 'ive', 'ic', 'ical', 'ize', 'ise', 'ist', 'or', 'ance',
                'ence', 'ant', 'ent', 'dom', 'ship', 'hood', 'ism', 'ee', 'eer', 'th',
                'ion', 's', 'teen', 'ty', 'y', 'en']
    # 常见前缀
    prefixes = ['un', 'dis', 're', 'pre', 'over', 'under', 'non', 'out', 'mis',
                'sub', 'super', 'inter', 'trans', 'semi', 'multi', 'mid', 'grand']

    # 1) word + suffix → 检查结果是否在词汇表中
    for suffix in suffixes:
        candidate = word_lower + suffix
        if candidate != word_lower and candidate in vocab:
            related.add(candidate)
        # 特殊：t/s 结尾的词加 ion（如 act→action, discuss→discussion）
        if suffix == 'ion' and word_lower.endswith('t'):
            candidate2 = word_lower + 'ion'
            if candidate2 != word_lower and candidate2 in vocab:
                related.add(candidate2)

    # 2) word 去掉后缀 → 检查词根是否在词汇表中，再用词根找其他派生词
    for suffix in suffixes:
        if word_lower.endswith(suffix) and len(word_lower) > len(suffix) + 2:
            stem = word_lower[:-len(suffix)]
            if len(stem) >= 3 and stem in vocab and stem != word_lower:
                related.add(stem)
                # 用同一词根找其他派生词
                for s2 in suffixes:
                    c2 = stem + s2
                    if c2 != word_lower and c2 in vocab:
                        related.add(c2)

    # 3) y → i 变体（如 happy → happiness, happily）
    if word_lower.endswith('y') and len(word_lower) > 2:
        stem_i = word_lower[:-1] + 'i'
        for suffix in ['ness', 'ly', 'er', 'est', 'ed', 'es']:
            c = stem_i + suffix
            if c != word_lower and c in vocab:
                related.add(c)
        stem_no_y = word_lower[:-1]
        for suffix in ['ied', 'ies', 'ier', 'iest', 'ily']:
            c = stem_no_y + suffix
            if c != word_lower and c in vocab:
                related.add(c)

    # 4) e 结尾变体（如 make → making, making → make）
    if word_lower.endswith('e') and len(word_lower) > 2:
        stem_no_e = word_lower[:-1]
        for suffix in ['ing', 'ed', 'able', 'er', 'est', 'ion', 'ity', 'ive']:
            c = stem_no_e + suffix
            if c != word_lower and c in vocab:
                related.add(c)

    # 5) 前缀变体：prefix + word → 检查是否在词汇表中
    for prefix in prefixes:
        candidate = prefix + word_lower
        if candidate != word_lower and candidate in vocab:
            related.add(candidate)

    # 6) 去前缀：如果 word 以某前缀开头，检查去掉前缀后的词根是否在词汇表中
    for prefix in sorted(prefixes, key=len, reverse=True):
        if word_lower.startswith(prefix) and len(word_lower) > len(prefix) + 2:
            stem = word_lower[len(prefix):]
            if len(stem) >= 3 and stem in vocab and stem != word_lower:
                related.add(stem)

    # 7) 双写变体（如 swim → swimming, running → run）
    if len(word_lower) >= 3 and word_lower[-1] in 'bdfgklmnprt':
        for suffix in ['ing', 'ed', 'er', 'est']:
            c = word_lower + word_lower[-1] + suffix
            if c != word_lower and c in vocab:
                related.add(c)
    if len(word_lower) >= 5 and word_lower[-2] == word_lower[-3]:
        for suffix in ['ing', 'ed', 'er', 'est']:
            if word_lower.endswith(suffix):
                stem = word_lower[:-len(suffix) - 1]
                if len(stem) >= 3 and stem in vocab and stem != word_lower:
                    related.add(stem)

    # 8) 已知复合词白名单（仅收录语义上确实同族的复合词）
    compound_map = {
        'toothache': ['ache', 'tooth'],
        'stomachache': ['ache', 'stomach'],
        'headache': ['ache', 'head'],
        'rainbow': ['rain', 'bow'],
        'schoolbag': ['school', 'bag'],
        'grandfather': ['father', 'grand'],
        'grandmother': ['mother', 'grand'],
        'grandparent': ['parent', 'grand'],
        'granddaughter': ['daughter', 'grand'],
        'grandson': ['son', 'grand'],
        'watermelon': ['water', 'melon'],
        'birthday': ['day', 'birth'],
        'weekday': ['day', 'week'],
        'weekend': ['week', 'end'],
        'newspaper': ['news', 'paper'],
        'notebook': ['book', 'note'],
        'textbook': ['book', 'text'],
        'blackboard': ['board', 'black'],
        'classmate': ['class', 'mate'],
        'classroom': ['class', 'room'],
        'schoolmate': ['school', 'mate'],
        'roommate': ['room', 'mate'],
        'teammate': ['team', 'mate'],
        'workmate': ['work', 'mate'],
        'playmate': ['play', 'mate'],
        'keyboard': ['board', 'key'],
        'cupboard': ['board', 'cup'],
        'basketball': ['ball', 'basket'],
        'football': ['ball', 'foot'],
        'baseball': ['ball', 'base'],
        'volleyball': ['ball'],
        'handbag': ['hand', 'bag'],
        'handwriting': ['hand', 'write'],
        'handshake': ['hand', 'shake'],
        'headline': ['head', 'line'],
        'firewood': ['fire', 'wood'],
        'firework': ['fire', 'work'],
        'fireplace': ['fire', 'place'],
        'fireman': ['fire', 'man'],
        'firefighter': ['fire', 'fighter'],
        'waterfall': ['water', 'fall'],
        'grassland': ['grass', 'land'],
        'farmland': ['farm', 'land'],
        'hometown': ['home', 'town'],
        'homework': ['home', 'work'],
        'housework': ['house', 'work'],
        'workplace': ['work', 'place'],
        'workshop': ['work', 'shop'],
        'network': ['net', 'work'],
        'moonlight': ['moon', 'light'],
        'sunlight': ['sun', 'light'],
        'sunshine': ['sun'],
        'sunrise': ['sun', 'rise'],
        'sunset': ['sun', 'set'],
        'sunflower': ['sun', 'flower'],
        'afternoon': ['noon', 'after'],
        'underground': ['under', 'ground'],
        'understand': ['under', 'stand'],
        'watermelon': ['water', 'melon'],
        'seashell': ['sea', 'shell'],
        'seaweed': ['sea', 'weed'],
        'seashore': ['sea', 'shore'],
        'coastline': ['coast', 'line'],
        'airport': ['air', 'port'],
        'passport': ['pass', 'port'],
        'seaport': ['sea', 'port'],
        'fingerprint': ['finger', 'print'],
        'footprint': ['foot', 'print'],
        'toothbrush': ['tooth', 'brush'],
        'toothpaste': ['tooth', 'paste'],
        'toothpick': ['tooth', 'pick'],
        'haircut': ['hair', 'cut'],
        'bookmark': ['book', 'mark'],
        'bookshop': ['book', 'shop'],
        'bookstore': ['book', 'store'],
        'crossword': ['word', 'cross'],
        'password': ['word', 'pass'],
        'keyword': ['word', 'key'],
        'framework': ['work', 'frame'],
        'homeland': ['home', 'land'],
        'homesick': ['home', 'sick'],
        'homeless': ['home', 'less'],
        'southeast': ['south', 'east'],
        'southwest': ['south', 'west'],
        'northeast': ['north', 'east'],
        'northwest': ['north', 'west'],
        'eastern': ['east'],
        'western': ['west'],
        'northern': ['north'],
        'southern': ['south'],
        'whenever': ['when', 'ever'],
        'whatever': ['what', 'ever'],
        'wherever': ['where', 'ever'],
        'whoever': ['who', 'ever'],
        'however': ['how', 'ever'],
        # 数词（不规则变形）
        'eighteen': ['eight'],
        'eighty': ['eight'],
        'eighth': ['eight'],
        'fifteen': ['five'],
        'fifty': ['five'],
        'fifth': ['five'],
        'forty': ['four'],
        'fourteen': ['four'],
        'fourth': ['four'],
        'ninth': ['nine'],
        'ninety': ['nine'],
        'nineteen': ['nine'],
        'thirteen': ['three'],
        'thirty': ['three'],
        'third': ['three'],
        'twelve': ['two'],
        'twenty': ['two'],
        'twelfth': ['two'],
        'second': ['two'],
        'sixth': ['six'],
        'sixteen': ['six'],
        'sixty': ['six'],
        'tenth': ['ten'],
        'eleventh': ['eleven'],
        # every 系列
        'everybody': ['every', 'body'],
        'everyday': ['every', 'day'],
        'everyone': ['every', 'one'],
        'everything': ['every', 'thing'],
        'everywhere': ['every', 'where'],
        'nobody': ['no', 'body'],
        'nothing': ['no', 'thing'],
        'nowhere': ['no', 'where'],
        'anyone': ['any', 'one'],
        'anybody': ['any', 'body'],
        'anything': ['any', 'thing'],
        'anywhere': ['any', 'where'],
        'someone': ['some', 'one'],
        'somebody': ['some', 'body'],
        'something': ['some', 'thing'],
        'somewhere': ['some', 'where'],
        # 其他常见复合词
        'grassland': ['grass', 'land'],
        'farmland': ['farm', 'land'],
        'hometown': ['home', 'town'],
        'homeland': ['home', 'land'],
        'homework': ['home', 'work'],
        'housework': ['house', 'work'],
        'workplace': ['work', 'place'],
        'workshop': ['work', 'shop'],
        'network': ['net', 'work'],
        'mooncake': ['moon', 'cake'],
        'moonlight': ['moon', 'light'],
        'sunlight': ['sun', 'light'],
        'sunshine': ['sun'],
        'sunrise': ['sun', 'rise'],
        'sunset': ['sun', 'set'],
        'sunflower': ['sun', 'flower'],
        'afternoon': ['noon', 'after'],
        'underground': ['under', 'ground'],
        'understand': ['under', 'stand'],
        'waterfall': ['water', 'fall'],
        'coastline': ['coast', 'line'],
        'headline': ['head', 'line'],
        'timeline': ['time', 'line'],
        'lifestyle': ['life', 'style'],
        'lifetime': ['life', 'time'],
        'lifelong': ['life', 'long'],
        'worldwide': ['world', 'wide'],
        'wildlife': ['wild', 'life'],
        'daytime': ['day', 'time'],
        'firewood': ['fire', 'wood'],
        'firework': ['fire', 'work'],
        'fireplace': ['fire', 'place'],
        'fireman': ['fire', 'man'],
        'sneaker': ['sneak'],
        'sneakers': ['sneak'],
        'earphones': ['ear'],
        'headphones': ['head'],
        'strawberry': ['berry'],
        'blueberry': ['berry'],
        'blackberry': ['berry'],
        'peanut': ['nut', 'pea'],
        'coconut': ['nut'],
        'chestnut': ['nut'],
        'walnut': ['nut'],
        'postcode': ['post', 'code'],
        'barcode': ['bar', 'code'],
        'handbag': ['hand', 'bag'],
        'handwriting': ['hand', 'write'],
        'handshake': ['hand', 'shake'],
        'bookmark': ['book', 'mark'],
        'bookshop': ['book', 'shop'],
        'bookstore': ['book', 'store'],
        'crossword': ['word', 'cross'],
        'password': ['word', 'pass'],
        'keyword': ['word', 'key'],
        'framework': ['work', 'frame'],
        'homesick': ['home', 'sick'],
        'homeless': ['home', 'less'],
        'fingerprint': ['finger', 'print'],
        'footprint': ['foot', 'print'],
        'toothbrush': ['tooth', 'brush'],
        'toothpaste': ['tooth', 'paste'],
        'toothpick': ['tooth', 'pick'],
        'haircut': ['hair', 'cut'],
        'airport': ['air', 'port'],
        'passport': ['pass', 'port'],
        'seaport': ['sea', 'port'],
        'seashell': ['sea', 'shell'],
        'seaweed': ['sea', 'weed'],
        'seashore': ['sea', 'shore'],
        'keyboard': ['board', 'key'],
        'cupboard': ['board', 'cup'],
        'blackboard': ['board', 'black'],
        'basketball': ['ball', 'basket'],
        'football': ['ball', 'foot'],
        'baseball': ['ball', 'base'],
        'volleyball': ['ball'],
        'classmate': ['class', 'mate'],
        'classroom': ['class', 'room'],
        'schoolmate': ['school', 'mate'],
        'roommate': ['room', 'mate'],
        'teammate': ['team', 'mate'],
        'workmate': ['work', 'mate'],
        'playmate': ['play', 'mate'],
        'grandfather': ['father', 'grand'],
        'grandmother': ['mother', 'grand'],
        'grandparent': ['parent', 'grand'],
        'granddaughter': ['daughter', 'grand'],
        'grandson': ['son', 'grand'],
        'rainbow': ['rain', 'bow'],
        'schoolbag': ['school', 'bag'],
        'watermelon': ['water', 'melon'],
        'birthday': ['day', 'birth'],
        'weekday': ['day', 'week'],
        'weekend': ['week', 'end'],
        'newspaper': ['news', 'paper'],
        'notebook': ['book', 'note'],
        'textbook': ['book', 'text'],
        'toothache': ['ache', 'tooth'],
        'stomachache': ['ache', 'stomach'],
        'headache': ['ache', 'head'],
        'southeast': ['south', 'east'],
        'southwest': ['south', 'west'],
        'northeast': ['north', 'east'],
        'northwest': ['north', 'west'],
        'sometimes': ['time'],
        'sometime': ['time'],
        'timepiece': ['time', 'piece'],
        'strawberry': ['berry'],
        'blueberry': ['berry'],
        'blackberry': ['berry'],
        'peanut': ['nut', 'pea'],
        'coconut': ['nut'],
        'chestnut': ['nut'],
        'walnut': ['nut'],
        'postcode': ['post', 'code'],
        'barcode': ['bar', 'code'],
        'lifestyle': ['life', 'style'],
        'lifetime': ['life', 'time'],
        'lifelong': ['life', 'long'],
        'worldwide': ['world', 'wide'],
        'wildlife': ['wild', 'life'],
        'daytime': ['day', 'time'],
        'nighttime': ['night', 'time'],
        'timeline': ['time', 'line'],
        'sometimes': ['time'],
        'sometime': ['time'],
        'timepiece': ['time', 'piece'],
        'earphones': ['ear'],
        'headphones': ['head'],
        'sneaker': ['sneak'],
        'sneakers': ['sneak'],
        'granny': ['grand'],
    }
    # 正向：如果 word 是复合词，连接其组成部分
    if word_lower in compound_map:
        for part in compound_map[word_lower]:
            if part in vocab and part != word_lower:
                related.add(part)
    # 反向：如果 word 是某个复合词的组成部分
    for compound, parts in compound_map.items():
        if word_lower in parts and compound in vocab and compound != word_lower:
            related.add(compound)
    # 同族连接：共享同一组成部分的复合词互连（如 grandfather↔grandmother 通过 grand）
    if word_lower in compound_map:
        my_parts = set(compound_map[word_lower])
        for compound, parts in compound_map.items():
            if compound == word_lower or compound not in vocab:
                continue
            shared = my_parts & set(parts)
            if shared:
                related.add(compound)

    return sorted(related)


def parse_vocab(md_text):
    """解析深圳中考词汇表，返回 {word: (phonetic, meaning)}"""
    vocab = {}
    for line in md_text.split('\n'):
        line = line.strip()
        if not line.startswith('|'): continue
        cells = [c.strip() for c in line.split('|')[1:-1]]
        if len(cells) < 4: continue
        try: int(cells[0])
        except ValueError: continue
        word = cells[1].split('(')[0].strip().lower()
        if not word or not word.isalpha(): continue
        phon = cells[2].strip().strip('"').strip("'")
        while len(phon) >= 2 and phon.startswith('[') and phon.endswith(']'):
            phon = phon[1:-1].strip()
        vocab[word] = (phon, cells[3])
    return vocab


def parse_vocab_extra(md_text):
    """解析词汇表.md（新课标2000词格式），返回 {word: (phonetic, meaning)}"""
    vocab = {}
    for line in md_text.split('\n'):
        line = line.strip()
        if not line.startswith('- **'): continue
        # 格式: - **word** [phon]  meaning
        rest = line[4:]  # 去掉 "- **"
        if '**' not in rest: continue
        word_part = rest.split('**')[0].strip().lower()
        if not word_part or not word_part.isalpha(): continue
        remainder = rest.split('**', 2)[-1].strip()
        # 提取音标
        phon = ''
        meaning = remainder
        if remainder.startswith('['):
            bracket_end = remainder.find(']')
            if bracket_end > 0:
                phon = remainder[1:bracket_end].strip()
                meaning = remainder[bracket_end+1:].strip()
        if word_part not in vocab:
            vocab[word_part] = (phon, meaning)
    return vocab


def parse_cards(md_text, batch_key):
    """解析联想记忆卡片，返回主词条列表（含词族联想）"""
    cards = []
    cur = None
    sub = None
    for line in (md_text or '').split('\n'):
        # 支持两种格式：## word (双井号) 和 ### word (三井号)
        if line.startswith('## '):
            # 处理双井号格式（如联想记忆卡片.md）
            cur = {'word': line[3:].strip(), 'phonetic': '', 'meaning': '',
                   'family': [], 'mnemonic': '', 'batch': batch_key}
            cards.append(cur)
            sub = None
        elif line.startswith('### '):
            # 处理三井号格式（如联想记忆卡片_A-B.md等）
            cur = {'word': line[4:].strip(), 'phonetic': '', 'meaning': '',
                   'family': [], 'mnemonic': '', 'batch': batch_key}
            cards.append(cur)
            sub = None
        elif line.startswith('#### ') and cur:
            sub = {'word': line[5:].strip(), 'phonetic': '', 'meaning': ''}
            cur['subs'] = cur.get('subs', [])
            cur['subs'].append(sub)
        elif cur:
            m = re.match(r'^- \*\*音标\*\*:\s*(.*)$', line)
            if m: (sub or cur)['phonetic'] = m[1].strip(); continue
            m = re.match(r'^- \*\*释义\*\*:\s*(.*)$', line)
            if m: (sub or cur)['meaning'] = m[1].strip(); continue
            m = re.match(r'^- \*\*词族联想\*\*:\s*(.*)$', line)
            if m: cur['family'] = [w.strip() for w in m[1].split(',') if w.strip()]; sub = None; continue
            m = re.match(r'^- \*\*记忆口诀\*\*:\s*(.*)$', line)
            if m: cur['mnemonic'] = m[1].strip(); sub = None; continue
    return [c for c in cards if c['word'] and c['word'].isalpha()]


def get_batch(word):
    """根据单词首字母确定批次"""
    w = word.lower().strip()
    if not w: return ''
    first = w[0]
    if first in 'abcd': return 'A-B' if first in 'ab' else 'C' if first == 'c' else 'D-M'
    if first in 'defghijklm': return 'D-M'
    if first in 'nopqr': return 'N-R'
    if first == 's': return 'S'
    if first == 't': return 'T'
    if first == 'u': return 'U'
    if first == 'v': return 'V'
    if first == 'w': return 'W'
    if first in 'yz': return 'Y' if first == 'y' else 'Z'
    return ''


def is_likely_real_word(word, vocab=None):
    """加强版启发式过滤：排除明显非法的衍生词"""
    if len(word) < 3:
        return False
    w = word.lower()
    # 保证收录白名单：已知合法但词根不在词汇表中的派生词
    guaranteed_words = {
        'unfold', 'unlikely', 'unknown', 'unfinished',
        'predict', 'prefer', 'preview',
        'unlike', 'united', 'unfair', 'unhappy', 'unable',
        'understand', 'understood', 'underground',
        'discover', 'discovered', 'discovery', 'disappoint',
        'disappear', 'disappointed', 'disappointing',
        'disagree', 'disagreement',
        'dismiss', 'dismissed',
        'prevent', 'prevented',
        'prepare', 'prepared', 'preparation',
        'return', 'returned',
        'outside', 'outlined', 'outline',
        'output', 'outputs',
        'rebuild', 'rebuilt', 'rewrite', 'rewritten',
        'redo', 'redone', 'react', 'reacted',
        'unlock', 'unlocked', 'unlocking',
        'undo', 'undone',
        'uncover', 'uncovered',
        'undress', 'undressed',
        'uneasy',
        'dislike', 'disliked',
        'dishonest', 'dishonesty',
        'disorder', 'disordered',
        'displease', 'displeased', 'displeasing',
        'dispose', 'disposed',
        'disprove', 'disproved',
        'disrespect', 'disrespected',
        'disrupt', 'disrupted',
        'distract', 'distracted',
        'overact', 'overacted',
        'overcome', 'overcame', 'overcome',
        'overhear', 'overheard',
        'overlook', 'overlooked',
        'overthrow', 'overthrown',
        'overeat', 'overeaten',
        'overuse', 'overused',
        'overdo', 'overdone',
        'overpay', 'overpaid',
        'overthink', 'overthought',
        'outlive', 'outlived',
        'outperform', 'outperformed',
        'outnumber', 'outnumbered',
        'outrun', 'outran', 'outrun',
        'outsmart', 'outsmarted',
        'overheat', 'overheated',
        'overrate', 'overrated',
        'override', 'overridden',
        'overeat', 'overeaten',
    }
    if w in guaranteed_words:
        return True
    # 明显非法模式：连续重复字母
    bad_patterns = ['xx', 'yy', 'zz', 'aa', 'ii']
    for p in bad_patterns:
        if p in w:
            return False
    # 多个后缀连缀
    if len(w) > 12:
        suffix_count = 0
        for s in ['ability', 'ization', 'tion', 'ness', 'ment', 'able', 'ible', 'ly', 'er', 'est']:
            if w.endswith(s):
                suffix_count += 1
        if suffix_count >= 2:
            return False
    # mis- 前缀一律拒绝
    if w.startswith('mis') and len(w) > 3:
        return False
    # 反身代词、时间名词、代词一律拒绝（含前缀叠加的情况）
    for forbidden in _is_invalid_stem_words():
        if w == forbidden or w.startswith(forbidden):
            return False
    # 已知绝对假词黑名单（持续累积）
    absolute_fakes = {
        'ununderstand', 'disunhappy', 'birthdayless', 'weekendment',
        'disachieve', 'unaddress', 'overaddress', 'unabroad', 'disabroad',
        'overabroad', 'underabroad', 'unadult', 'disadult', 'overadult',
        'underadult', 'unago', 'disago', 'overago', 'underago',
        'unagain', 'disagain', 'overagain', 'underagain',
        'unage', 'disage', 'overage', 'underage',
        'unair', 'disair', 'overair', 'underair',
        'unafrican', 'disafrican', 'overafrican', 'underafrican',
        'unamerica', 'disamerica', 'overamerica', 'underamerica',
        'unamerican', 'disamerican', 'overamerican', 'underamerican',
        'unancient', 'disancient', 'overancient', 'underancient',
        'unangry', 'disangry', 'overangry', 'underangry',
        'unanimal', 'disanimal', 'overanimal', 'underanimal',
        'unanswer', 'disanswer', 'overanswer', 'underanswer',
        'unany', 'disany', 'overany', 'underany',
        'unanybody', 'disanybody', 'overanybody', 'underanybody',
        'unapple', 'disapple', 'overapple', 'underapple',
        'unarea', 'disarea', 'overarea', 'underarea',
        'unarmy', 'disarmy', 'overarmy', 'underarmy',
        'unasia', 'disasia', 'overasia', 'underasia',
        'unasian', 'disasian', 'overasian', 'underasian',
        'unasleep', 'disasleep', 'overasleep', 'underasleep',
        'unaugust', 'disaugust', 'overaugust', 'underaugust',
        'unaunt', 'disaunt', 'overaunt', 'underaunt',
        'unaustralia', 'disaustralia', 'overaustralia', 'underaustralia',
        'unabout', 'overabout', 'underabout',
        'unability', 'overability', 'underability',
        'preabsent', 'underaccident', 'disactivity',
        'underyourself', 'unyourself', 'yesterdayer',
        'mondayless', 'misrainy', 'misunderstandable',
        'unMonday', 'unweekend', 'misagree',
        'underable', 'overable', 'preable',
        'underactress', 'underadd',
    }
    if w in absolute_fakes:
        return False
    # 双重前缀拒绝（如 ununderstand, disunhappy）
    double_prefixes = ['un', 'dis', 'over', 'under', 'pre', 'non', 'out', 're']
    for dp in double_prefixes:
        rest = w[len(dp):]
        for dp2 in double_prefixes:
            if rest.startswith(dp2) and len(rest) - len(dp2) >= 2:
                return False
    # 对每个前缀依次尝试匹配
    for prefix in sorted(['under', 'over', 'non', 'pre', 'out', 're', 'dis', 'un'], key=len, reverse=True):
        if w.startswith(prefix) and len(w) > len(prefix):
            stem = w[len(prefix):]
            if len(stem) < 2:
                return False
            # 词根本身是无效词根则拒绝
            if not _is_valid_stem(stem):
                return False
            # 名词词根拒绝后缀
            _noun_suffixes = ['ity', 'ty', 'tion', 'sion', 'ness', 'ment',
                              'ence', 'ance', 'ship', 'dom', 'hood', 'ism',
                              'ist', 'or', 'ent', 'ee', 'eer', 'ette', 'let', 'ling']
            # pre- 白名单
            if prefix == 'pre':
                pre_whitelist = {
                    'prepare', 'predict', 'prevent', 'prefer', 'preview', 'preach',
                    'preserve', 'precise', 'prejudice', 'preliminary', 'premier',
                    'premise', 'preoccupy', 'preorder', 'prehistoric', 'preschool',
                    'president', 'prerequisite', 'pressure', 'prevention',
                    'preheat', 'prepay', 'pretest', 'pretrain', 'preset',
                    'pregame', 'prelaunch', 'prelude', 'premarital', 'premature',
                    'premiere', 'preponder', 'preposition', 'preposter', 'prerogative',
                    'presage', 'prescind', 'prescribe', 'presence', 'present',
                    'presto', 'pretax', 'preteen', 'preterm', 'pretrial',
                    'prettify', 'prevaricate', 'prevail', 'prevalence', 'preverb',
                    'prevolve', 'prewar', 'prewise', 'prewrite',
                }
                if w not in pre_whitelist:
                    for ns in _noun_suffixes:
                        if stem.endswith(ns) and len(stem) - len(ns) >= 2:
                            continue  # 词根不合格，尝试更短前缀
                    return False
                break
            # re-/out- 白名单
            if prefix in ('re', 'out'):
                common_re_out = {
                    'redo', 'react', 'rebuild', 'rewrite', 'return',
                    'output', 'outline', 'outlive', 'outperform', 'outnumber',
                    'reveal', 'repeat', 'replace', 'report', 'request',
                    'require', 'research', 'respect', 'respond', 'rest',
                    'result', 'return', 'reuse', 'reverse', 'review',
                    'revolution', 'reward', 'ring', 'rise', 'run',
                    'outside', 'outlook', 'output', 'outreach', 'outrun',
                }
                if w in common_re_out:
                    break
                if vocab and stem not in vocab:
                    continue  # 词根不在vocab，尝试更短前缀
                if len(stem) <= 3 and (not vocab or stem not in vocab):
                    continue  # 短词根不在vocab，尝试更短前缀
                for ns in _noun_suffixes:
                    if stem.endswith(ns) and len(stem) - len(ns) >= 2:
                        continue  # 名词词根，尝试更短前缀
                break
            # un-/dis- 白名单 + 短词根拒绝
            if prefix in ('un', 'dis'):
                common_un_dis = {
                    'unable', 'unfair', 'unhappy', 'unknown', 'unlikely', 'unusual',
                    'unfit', 'unfinished', 'unfold', 'undo', 'unite', 'unlock',
                    'uncover', 'understand', 'undress', 'uneasy',
                    'dislike', 'disagree', 'disappear', 'discover', 'dishonest',
                    'disorder', 'dismiss', 'displease', 'dispose', 'disprove',
                    'disrespect', 'disrupt', 'distract',
                }
                if w in common_un_dis:
                    break
                # 短词根拒绝（≤3字母且不在vocab中），但已在白名单的除外
                if len(stem) <= 3 and (not vocab or stem not in vocab):
                    continue  # 短词根不在vocab，尝试更短前缀
                for ns in _noun_suffixes:
                    if stem.endswith(ns) and len(stem) - len(ns) >= 2:
                        continue  # 名词词根，尝试更短前缀
                break
            # under-/over-/non-：词根必须在vocab中 + 名词词根拒绝 + 短词根拒绝
            if vocab and stem not in vocab:
                found = False
                for sfx in ['able', 'ful', 'ly', 'ness', 'ment', 'tion', 'sion', 'al', 'ic', 'ive', 'ous']:
                    if stem.endswith(sfx) and len(stem) - len(sfx) >= 2:
                        if vocab and (stem[:-len(sfx)] in vocab):
                            found = True
                            break
                if not found:
                    continue  # 词根不在vocab，尝试更短前缀
            # 短词根拒绝：≤3字母且不在vocab中
            if len(stem) <= 3 and (not vocab or stem not in vocab):
                continue  # 短词根不在vocab，尝试更短前缀
            # 名词后缀拒绝
            for ns in _noun_suffixes:
                if stem.endswith(ns) and len(stem) - len(ns) >= 2:
                    continue  # 名词词根，尝试更短前缀
            break
    return True


def _is_invalid_stem_words():
    """返回所有禁止作为词根的单词集合（反身代词、代词、时间名词）"""
    return {
        # 反身代词
        'myself', 'yourself', 'himself', 'herself', 'itself',
        'ourselves', 'yourselves', 'themselves',
        # 代词
        'i', 'me', 'my', 'you', 'your', 'he', 'him', 'his',
        'she', 'her', 'it', 'its', 'we', 'us', 'our',
        'they', 'them', 'their',
        'who', 'whom', 'whose', 'what', 'which',
        'that', 'this', 'these', 'those',
        'one', 'ones',
        # 时间名词
        'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
        'yesterday', 'today', 'tomorrow', 'tonight', 'weekend', 'weekday',
        'daybeforeyesterday', 'midweek', 'week',
    }


def fetch_my_memory(word):
    """调用 MyMemory 翻译 API 获取中文释义（国内可用），返回 meaning 字符串"""
    import time as _time
    for attempt in range(5):
        try:
            url = f"https://api.mymemory.translated.net/get?q={word}&langpair=en|zh"
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json'
            })
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode())
            result = data.get('responseData', {})
            text = result.get('translatedText', '').strip()
            # 过滤掉原文本身（翻译 API 对已知词会返回原文）
            if text.lower() == word:
                return ''
            return text
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < 4:
                wait = 6 * (2 ** attempt)
                print(f"  [MyMemory 限流 {e.code}] {word}，等待 {wait}s 后重试 ({attempt+1}/5)...")
                _time.sleep(wait)
                continue
            print(f"  [MyMemory 失败] {word}: HTTP {e.code}")
            return ''
        except Exception as e:
            if attempt < 4:
                wait = 4 * (2 ** attempt)
                print(f"  [MyMemory 网络错误] {word}: {e}，等待 {wait}s 后重试...")
                _time.sleep(wait)
                continue
            print(f"  [MyMemory 失败] {word}: {e}")
            return ''
            return ''
    return ''


def derive_phonetic(root_word, root_phonetic, family_word):
    """基于词根音标推导词族词的音标（简单规则）"""
    if not root_phonetic:
        return ''
    # 常见后缀对应的音标添加规则
    suffix_phon_map = {
        'ing': 'ɪŋ', 'ed': 'd', 's': 'z', 'es': 'z',
        'ly': 'li', 'er': 'ə(r)', 'est': 'ɪst',
        'tion': 'ʃən', 'sion': 'ʒən', 'ment': 'mənt',
        'ance': 'əns', 'ence': 'əns', 'ness': 'nis',
        'able': 'əbl', 'ible': 'əbl', 'al': 'əl',
        'ic': 'ɪk', 'ive': 'ɪv', 'ful': 'fʊl',
        'less': 'ləs', 'ous': 'əs', 'ize': 'aɪz',
        'ise': 'aɪz', 'y': 'i', 'ies': 'iz',
        'ier': 'ɪə(r)', 'iest': 'ɪɪst',
    }
    # 尝试匹配最长后缀
    for suffix, phon_suffix in sorted(suffix_phon_map.items(), key=lambda x: -len(x[0])):
        if family_word.endswith(suffix) and len(family_word) > len(suffix) + 2:
            stem = family_word[:-len(suffix)]
            # 简单处理：去掉词根末尾静音e后加后缀音标
            if root_word.endswith('e') and not family_word.endswith('e'):
                base = root_phonetic.rstrip('e').rstrip()
            else:
                base = root_phonetic
            return (base + phon_suffix).strip()
    return root_phonetic


def derive_meaning(root_meaning, family_word):
    """基于词根释义和词族词的后缀，推导词族词释义"""
    if not root_meaning:
        return ''
    # 按后缀长度降序匹配
    suffix_rules = [
        ('ing', 'v.', 'adj.'),
        ('ed', 'v.', ''),
        ('s', '', ''),
        ('es', '', ''),
        ('ly', 'adv.', ''),
        ('er', 'n.', ''),
        ('est', 'adj.', 'adv.'),
        ('tion', 'n.', ''),
        ('sion', 'n.', ''),
        ('ment', 'n.', ''),
        ('ance', 'n.', ''),
        ('ence', 'n.', ''),
        ('ness', 'n.', ''),
        ('able', 'adj.', ''),
        ('ible', 'adj.', ''),
        ('al', 'adj.', ''),
        ('ic', 'adj.', ''),
        ('ive', 'adj.', ''),
        ('ful', 'adj.', ''),
        ('less', 'adj.', ''),
        ('ous', 'adj.', ''),
        ('ize', 'v.', ''),
        ('ise', 'v.', ''),
        ('y', 'n.', 'v.'),
        ('ies', 'n.', 'v.'),
        ('ier', 'n.', ''),
        ('iest', 'adj.', ''),
    ]
    for suffix, pos1, pos2 in suffix_rules:
        if family_word.endswith(suffix) and len(family_word) > len(suffix) + 2:
            # 提取词根部分
            stem = family_word[:-len(suffix)]
            # 替换词性前缀
            new_meaning = re.sub(r'^(n\.|v\.|adj\.|adv\.|prep\.|conj\.|pron\.|int\.|art\.)+', pos1, root_meaning)
            if pos2 and not new_meaning.startswith(pos2):
                # 在原释义前追加另一种词性
                new_meaning = pos2 + new_meaning.lstrip(pos1).lstrip(pos2)
            # 尝试从词根含义中提取核心中文意思
            # 移除英文词性标记，保留中文释义部分
            core = re.sub(r'^(n\.|v\.|adj\.|adv\.|prep\.|conj\.|pron\.|int\.|art\.)+(.*?)(?:\s*[；;]\s*(n\.|v\.|adj\.|adv\.|prep\.|conj\.|pron\.|int\.|art\.)+.*)*$', r'\2', new_meaning)
            core = core.strip()
            if core and len(core) > 1:
                return pos1 + core
            return new_meaning
    # 无匹配后缀，直接返回词根释义
    return root_meaning


def generate_example(word, meaning):
    """根据单词和释义生成示例例句"""
    if not word or not meaning:
        return ''
    word = word.lower()
    meaning_clean = re.sub(r'^(n\.|v\.|adj\.|adv\.|prep\.|conj\.|pron\.|int\.|art\.)+', '', meaning).strip()
    
    # 动词示例模板
    if meaning.startswith('v.') or 'v.' in meaning[:5]:
        templates = [
            f"The {word} is very important.",
            f"People {word} every day.",
            f"I like to {word}.",
            f"They will {word} tomorrow.",
            f"He {word}s often.",
        ]
        return f"📝 {templates[0]}"
    
    # 名词示例模板
    if meaning.startswith('n.') or 'n.' in meaning[:5]:
        templates = [
            f"This is a good {word}.",
            f"I have a {word}.",
            f"The {word} is interesting.",
            f"Many {word}s exist.",
        ]
        return f"📝 {templates[0]}"
    
    # 形容词示例模板
    if meaning.startswith('adj.') or 'adj.' in meaning[:5]:
        templates = [
            f"It is very {word}.",
            f"The {word} day was great.",
            f"She looks {word}.",
            f"This is {word} enough.",
        ]
        return f"📝 {templates[0]}"
    
    # 副词示例模板
    if meaning.startswith('adv.') or 'adv.' in meaning[:5]:
        templates = [
            f"He runs {word}.",
            f"She sings {word}.",
            f"They arrived {word}.",
        ]
        return f"📝 {templates[0]}"
    
    # 默认示例
    return f"📝 This is an example of '{word}'."


def main():
    print("正在解析深圳中考词汇表...")
    with open(VOCAB_FILE, encoding='utf-8') as f:
        vocab = parse_vocab(f.read())
    print(f"  主词汇表: {len(vocab)} 词")
    # 合并新课标2000词词汇表
    extra_file = os.path.join(DICT_DIR, '词汇表.md')
    if os.path.exists(extra_file):
        with open(extra_file, encoding='utf-8') as f:
            extra_vocab = parse_vocab_extra(f.read())
        before = len(vocab)
        for w, (p, m) in extra_vocab.items():
            if w not in vocab:
                vocab[w] = (p, m)
        print(f"  新课标补充: +{len(vocab) - before} 词（合计 {len(vocab)} 词）")

    print("\n正在解析联想记忆卡片...")
    card_map = {}
    for batch_key, fname in CARD_FILES:
        fp = os.path.join(DICT_DIR, fname)
        if not os.path.exists(fp): continue
        with open(fp, encoding='utf-8') as f:
            md = f.read()
        cards = parse_cards(md, batch_key)
        for c in cards:
            card_map[c['word'].lower()] = c
        print(f"  {fname}: {len(cards)} 词")

    # 构建主节点（全量词汇表，只收录真实存在的单词）
    nodes = []
    edges = []
    node_id_map = {}
    next_id = 0
    edge_set = set()  # 去重

    for word, (phon, meaning) in sorted(vocab.items(), key=lambda x: x[0]):
        nid = str(next_id)
        node_id_map[word] = nid
        batch = get_batch(word)
        card = card_map.get(word, {})
        nodes.append({
            'id': nid, 'label': word, 'type': 'main',
            'phonetic': phon, 'meaning': meaning,
            'batch': batch,
            'mnemonic': card.get('mnemonic', ''),
            'example': generate_example(word, meaning)
        })
        next_id += 1

    # 构建词族边：只连接词汇表中已存在的单词
    for word in vocab:
        nid = node_id_map[word]
        # 1) 卡片中明确标注的词族联想（只保留词汇表中存在的）
        card = card_map.get(word, {})
        family_words = list(dict.fromkeys(card.get('family', [])))
        for fw in family_words:
            fw_clean = re.sub(r'[^a-zA-Z]', '', fw).lower()
            if not fw_clean or fw_clean == word or fw_clean not in vocab:
                continue
            nid_fw = node_id_map.get(fw_clean)
            if not nid_fw:
                continue
            key = tuple(sorted([nid, nid_fw]))
            if key not in edge_set:
                edge_set.add(key)
                edges.append({'source': nid, 'target': nid_fw, 'label': '词族'})
        # 2) 自动匹配：在词汇表中找同词族的词（前缀/后缀/词根匹配）
        related = find_vocab_family(word, vocab)
        for rw in related:
            if rw == word or rw not in node_id_map:
                continue
            nid_rw = node_id_map[rw]
            key = tuple(sorted([nid, nid_rw]))
            if key not in edge_set:
                edge_set.add(key)
                edges.append({'source': nid, 'target': nid_rw, 'label': '词族'})

    # 统计
    batch_counts = Counter(n['batch'] for n in nodes)
    batches = {k: {'color': BATCH_COLORS.get(k, '#fbbf24'), 'count': batch_counts.get(k, 0)}
               for k in BATCH_COLORS}

    out = {
        'meta': {'total': len(nodes), 'edges': len(edges)},
        'nodes': nodes, 'edges': edges, 'batches': batches
    }

    with open(OUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 已写入 {OUT_FILE}")
    print(f"   节点: {len(nodes)} (全部为词汇表真实单词，无造词)")
    print(f"   边: {len(edges)}")
    print(f"   批次分布: {dict(batch_counts)}")


if __name__ == '__main__':
    main()
