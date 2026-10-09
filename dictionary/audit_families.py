"""全面审计词族关系：检查遗漏、错误、统计覆盖率"""
import json
from collections import defaultdict

with open(r'd:\project\math-visualization\public\vocab_cards.json', encoding='utf-8-sig') as f:
    d = json.load(f)

nodes_by_id = {n['id']: n for n in d['nodes']}
nodes_by_label = {n['label']: n for n in d['nodes']}
edges = d['edges']
batch_map = {n['label']: n.get('batch', '') for n in d['nodes']}

# 构建邻接表（按 label）
adj = defaultdict(set)
for e in edges:
    s = nodes_by_id.get(e['source'], {}).get('label', '')
    t = nodes_by_id.get(e['target'], {}).get('label', '')
    if s and t:
        adj[s].add(t)
        adj[t].add(s)

total = len(d['nodes'])
has_family = sum(1 for w in adj if adj[w])
no_family = sorted([n['label'] for n in d['nodes'] if n['label'] not in adj])

print(f'总词数: {total}')
print(f'有词族关联: {has_family}')
print(f'无词族关联: {len(no_family)}')
print(f'总边数: {len(edges)}')

# 词族大小分布
sizes = defaultdict(int)
for w in adj:
    sizes[len(adj[w])] += 1
print(f'\n词族大小分布:')
for s in sorted(sizes.keys()):
    print(f'  {s}个关联: {sizes[s]}个词')

# 各批次抽样
batches = defaultdict(list)
for w in adj:
    batches[batch_map[w]].append((w, sorted(adj[w])))

print(f'\n=== 各批次抽样（每批前8个有词族的词）===')
for batch in sorted(batches.keys()):
    items = sorted(batches[batch])[:8]
    print(f'\n[{batch}] ({len(batches[batch])}个有词族关联)')
    for w, fam in items:
        print(f'  {w} -> {fam}')

# 检查可能的遗漏：4字母前缀相同的词组
print(f'\n=== 检查可能的遗漏（3+词共享4字母前缀但未全部连接）===')
prefix_groups = defaultdict(list)
for w in nodes_by_label:
    if len(w) >= 5:
        prefix_groups[w[:4]].append(w)

missing_count = 0
for prefix in sorted(prefix_groups.keys()):
    words = sorted(prefix_groups[prefix])
    if len(words) >= 3:
        missing = []
        for i, w1 in enumerate(words):
            for w2 in words[i+1:]:
                if w2 not in adj.get(w1, set()):
                    missing.append((w1, w2))
        if missing:
            missing_count += 1
            if missing_count <= 20:
                print(f'  词根"{prefix}": {words}')
                print(f'    缺失: {missing[:3]}')
if missing_count > 20:
    print(f'  ... 共 {missing_count} 组有遗漏')

# 检查无词族的词
print(f'\n=== 无词族关联的词（前30个）===')
print(', '.join(no_family[:30]))
if len(no_family) > 30:
    print(f'  ... 共 {len(no_family)} 个')
