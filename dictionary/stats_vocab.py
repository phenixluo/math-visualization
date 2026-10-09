# -*- coding: utf-8 -*-
"""
统计词汇表信息
"""

import re
from pathlib import Path

def main():
    md_file = Path(__file__).parent / "词汇表.md"
    
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 统计词汇数
    words = re.findall(r'- \*\*([a-zA-Z]+)\*\*', content)
    total_words = len(words)
    
    # 按字母统计
    letters = {}
    current_letter = ""
    for word in words:
        first_letter = word[0].upper()
        if first_letter != current_letter:
            current_letter = first_letter
            letters[current_letter] = 0
        letters[current_letter] += 1
    
    # 输出统计
    print("=" * 60)
    print("词汇表统计报告")
    print("=" * 60)
    print(f"\n总词汇数: {total_words}")
    print(f"\n各字母词汇分布:")
    
    total = 0
    for letter in sorted(letters.keys()):
        count = letters[letter]
        total += count
        print(f"  {letter}: {count:3d} 词")
    
    print(f"\n总计: {total} 词")
    
    # 检查是否包含新课标词汇
    print("\n" + "=" * 60)
    print("新课标新增词汇检查（部分示例）")
    print("=" * 60)
    
    new_vocab_samples = ['account', 'AI', 'athlete', 'balance', 'challenge', 
                         'climate', 'digital', 'download', 'volunteer', 'youth']
    
    for word in new_vocab_samples:
        if word in words:
            print(f"  ✓ {word}")
        else:
            print(f"  ✗ {word} (缺失)")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
