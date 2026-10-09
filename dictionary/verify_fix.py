"""验证修复结果"""
import json, re, os

DICT_DIR = r'd:\project\math-visualization\dictionary'
OUT_FILE = os.path.join(DICT_DIR, 'vocab_cards.json')
PUBLIC_FILE = r'd:\project\math-visualization\public\vocab_cards.json'

with open(OUT_FILE, encoding='utf-8') as f:
    data = json.load(f)

nodes = data.get('nodes', [])
words = {n['label'].lower() for n in nodes}

# 已知假词
fakes = ['misrainy', 'unMonday', 'disunhappy', 'disactivity', 'underabout',
         'underable', 'overable', 'preable', 'underactress', 'underadd']

# 之前缺失的合法词
missing = ['unfold', 'unlikely', 'unknown', 'unfinished', 'predict', 'prefer', 'preview']

print(f"总节点数: {len(nodes)}")
print(f"总唯一词数: {len(words)}")
print()

# 假词检查
print("=== 假词检查 ===")
found_fakes = [w for w in fakes if w in words]
print(f"已知假词仍存在: {found_fakes if found_fakes else '无 ✓'}")

# 之前缺失的词
print()
print("=== 之前缺失的合法词 ===")
for w in missing:
    status = "✓ 已恢复" if w in words else "✗ 仍缺失"
    print(f"  {w}: {status}")

# 同步到 public
with open(PUBLIC_FILE, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"\n已同步到 public/vocab_cards.json")
