"""快速修正 vocab_cards.json 中的批次标签"""
import json, re

with open(r'd:\project\math-visualization\dictionary\vocab_cards.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 统计当前批次分布
from collections import Counter
batch_counts = Counter(n['batch'] for n in data['nodes'])
print("当前批次分布:", dict(batch_counts))
print("Q-Z 是否存在:", 'Q-Z' in batch_counts)
print("N-R 是否存在:", 'N-R' in batch_counts)

# 检查 edges 中的 source/target 是否是字符串 ID 或对象引用
sample_edge = data['edges'][0]
print("\n边示例:", sample_edge)
print("边 source 类型:", type(sample_edge.get('source')))
print("边 target 类型:", type(sample_edge.get('target')))
