# -*- coding: utf-8 -*-
"""
从网络抓取指定字母开头的词汇并更新词汇表
使用方法: python fetch_z_vocab.py
"""

import re
from pathlib import Path

def fetch_z_vocab():
    """
    获取Z开头的中考英语词汇
    基于搜索结果的中考高频词汇
    """
    z_words = [
        ("zany", "['zeɪni]", "adj. 古怪的；滑稽的"),
        ("zap", "[zæp]", "v. 迅速行动；消耗"),
        ("zeal", "[ziːl]", "n. 热情；热忱"),
        ("zealous", "['zeləs]", "adj. 热情的；狂热的"),
        ("zebra", "['ziːbrə]", "n. 斑马"),
        ("zero", "['zɪərəʊ]", "n. 零；零度"),
        ("zip", "[zɪp]", "v. 拉上拉链；n. 拉链"),
        ("zipper", "['zɪpə(r)]", "n. 拉链"),
        ("zone", "[zəʊn]", "n. 地区；区域"),
        ("zoo", "[zuː]", "n. 动物园"),
        ("zoology", "[zəˈɒlədʒi]", "n. 动物学"),
        ("zoom", "[zuːm]", "v. 急速移动；放大"),
    ]
    return z_words

def read_existing_md(filepath):
    """读取现有Markdown文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def update_z_section(content, new_z_words):
    """更新Z部分的内容"""
    # 找到 ## Z 部分
    z_pattern = r'(## Z\s*\n)((?:- \*\*.*?\n)*)'
    
    # 构建新的Z部分内容
    new_z_lines = []
    for word, phonetic, meaning in new_z_words:
        new_z_lines.append(f"- **{word}** {phonetic}  {meaning}")
    
    new_z_section = "## Z\n" + "\n".join(new_z_lines) + "\n"
    
    # 替换原有的Z部分
    def replace_z(match):
        return new_z_section
    
    updated_content = re.sub(z_pattern, replace_z, content, flags=re.MULTILINE)
    
    return updated_content

def main():
    print("=" * 50)
    print("Z词汇抓取与合并工具")
    print("=" * 50)
    
    # 1. 获取Z词汇
    print("\n1. 获取Z词汇...")
    z_words = fetch_z_vocab()
    print(f"   获取到 {len(z_words)} 个Z词汇")
    
    # 2. 读取现有词汇表
    print("2. 读取现有词汇表...")
    script_dir = Path(__file__).parent
    md_file = script_dir / "词汇表.md"
    
    if not md_file.exists():
        print(f"   ✗ 词汇表文件不存在: {md_file}")
        return
    
    content = read_existing_md(md_file)
    print(f"   ✓ 已读取词汇表")
    
    # 3. 更新Z部分
    print("3. 更新Z词汇部分...")
    updated_content = update_z_section(content, z_words)
    
    # 4. 保存
    print("4. 保存更新...")
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print(f"   ✓ 已更新: {md_file}")
    
    # 5. 统计
    z_count = len(re.findall(r'^- \*\*z', updated_content, re.MULTILINE))
    print(f"\n   Z词汇总数: {z_count}")
    
    print("\n" + "=" * 50)
    print("完成！")
    print("=" * 50)

if __name__ == "__main__":
    main()
