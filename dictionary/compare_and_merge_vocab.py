# -*- coding: utf-8 -*-
"""
对比广东省中考英语词汇表并补充缺失词汇
使用方法: python compare_and_merge_vocab.py
"""

import re
from pathlib import Path
from typing import List, Tuple, Set

def extract_words_from_html(html_file: Path) -> List[Tuple[str, str, str]]:
    """从HTML文件提取词汇"""
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    words = []
    
    # 方法1：查找表格中的词汇（序号、单词、音标、释义）
    # 匹配表格行模式
    table_pattern = r'<tr[^>]*>\s*<td[^>]*>(\d+)</td>\s*<td[^>]*>([a-zA-Z\s&]+?)</td>\s*<td[^>]*>(\[?[^\]]*\]?)</td>\s*<td[^>]*>(.+?)</td>'
    matches = re.findall(table_pattern, html_content, re.DOTALL)
    
    for match in matches:
        seq_num, word, phonetic, meaning = match
        word = word.strip()
        phonetic = phonetic.strip()
        meaning = meaning.strip()
        
        # 清理词汇中的多余空格和符号
        word = re.sub(r'\s+', ' ', word).strip()
        
        # 只保留有效的英语单词
        if word and re.match(r'^[a-zA-Z]+$', word):
            words.append((word, phonetic, meaning))
    
    print(f"从HTML提取到 {len(words)} 个词汇")
    
    # 如果表格提取失败，尝试其他方法
    if len(words) < 100:
        words = extract_words_by_text_pattern(html_content)
    
    return words

def extract_words_by_text_pattern(html_content: str) -> List[Tuple[str, str, str]]:
    """通过文本模式提取词汇"""
    words = []
    
    # 清理HTML标签获取纯文本
    text = re.sub(r'<[^>]+>', '\n', html_content)
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        # 匹配格式：序号 单词 音标 释义
        match = re.search(r'^(\d+)\s+([a-zA-Z]+)\s+(\[[^\]]+\])\s+(.+)$', line)
        if match:
            word = match.group(2)
            phonetic = match.group(3)
            meaning = match.group(4)
            words.append((word, phonetic, meaning))
    
    print(f"通过文本模式提取到 {len(words)} 个词汇")
    return words

def read_existing_vocab(md_file: Path) -> Set[str]:
    """读取现有词汇表中的词汇"""
    existing_words = set()
    
    if md_file.exists():
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 匹配 Markdown 格式的词汇
        pattern = r'- \*\*([a-zA-Z]+)\*\*'
        matches = re.findall(pattern, content)
        existing_words = set(matches)
    
    print(f"现有词汇表中有 {len(existing_words)} 个词汇")
    return existing_words

def merge_and_generate(md_file: Path, new_words: List[Tuple[str, str, str]]):
    """合并新词汇并生成Markdown"""
    # 读取现有内容
    if md_file.exists():
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        content = ""
    
    # 提取现有词汇
    existing_words = {}
    current_section = ""
    section_content = {}
    
    # 按章节分割
    sections = re.split(r'(^##\s+[A-Z])', content, flags=re.MULTILINE)
    
    for i, section in enumerate(sections):
        if section.startswith('##'):
            current_section = section.strip()
            section_content[current_section] = []
        elif current_section and section.strip():
            section_content[current_section].append(section)
            # 提取该章节的词汇
            matches = re.findall(r'- \*\*([a-zA-Z]+)\*\*', section)
            for word in matches:
                existing_words[word.lower()] = (word, "", "")
    
    # 添加新词汇
    added_count = 0
    for word, phonetic, meaning in new_words:
        word_lower = word.lower()
        if word_lower not in existing_words:
            existing_words[word_lower] = (word, phonetic, meaning)
            added_count += 1
    
    # 重新生成Markdown
    lines = [
        "# 深圳中考英语新课标2000词词汇表",
        "> 依据《义务教育英语课程标准》（2022年版）",
        "> 包含约1600个广东省中考考纲词汇及约400个新增词汇",
        "> 参考来源：广东省初中学业水平考试英语词汇表",
        ""
    ]
    
    current_letter = ""
    for word_lower, (word, phonetic, meaning) in sorted(existing_words.items(), key=lambda x: x[1][0].lower()):
        first_letter = word[0].upper()
        if first_letter != current_letter:
            current_letter = first_letter
            lines.append(f"## {current_letter}")
            lines.append("")
        lines.append(f"- **{word}** {phonetic}  {meaning}")
    
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    return len(existing_words), added_count

def main():
    print("=" * 60)
    print("广东省中考英语词汇表对比与合并工具")
    print("=" * 60)
    
    script_dir = Path(__file__).parent
    
    # 1. 从HTML提取词汇
    print("\n1. 从HTML文件提取词汇...")
    html_file = script_dir / "广东省中考英语词汇表.html"
    if not html_file.exists():
        print(f"   ✗ 找不到HTML文件: {html_file}")
        return
    
    gd_words = extract_words_from_html(html_file)
    if not gd_words:
        print("   ✗ 未能从HTML提取词汇")
        return
    
    print(f"   ✓ 成功提取 {len(gd_words)} 个广东省中考词汇")
    
    # 2. 读取现有词汇表
    print("\n2. 读取现有词汇表...")
    md_file = script_dir / "词汇表.md"
    existing_words = read_existing_vocab(md_file)
    
    # 3. 找出缺失的词汇
    print("\n3. 对比分析...")
    existing_set = set(w.lower() for w, _, _ in gd_words)
    missing_words = [(w, p, m) for w, p, m in gd_words if w.lower() not in existing_words]
    
    print(f"   广东省考纲词汇: {len(gd_words)} 词")
    print(f"   现有词汇表: {len(existing_words)} 词")
    print(f"   缺失词汇: {len(missing_words)} 词")
    
    # 4. 合并并生成
    print("\n4. 合并并生成新词汇表...")
    total_count, added_count = merge_and_generate(md_file, gd_words)
    
    print(f"   ✓ 已更新: {md_file}")
    print(f"   ✓ 总词汇数: {total_count}")
    print(f"   ✓ 新增词汇: {added_count}")
    
    # 5. 保存到vocab_data.py
    print("\n5. 保存至vocab_data.py...")
    data_file = script_dir / "vocab_data.py"
    with open(data_file, 'w', encoding='utf-8') as f:
        f.write("# -*- coding: utf-8 -*-\n")
        f.write("# 深圳中考英语新课标词汇表（自动生成）\n\n")
        f.write("VOCAB_DATA = [\n")
        for word_lower, (word, phonetic, meaning) in sorted(existing_words.items(), key=lambda x: x[1][0].lower()):
            f.write(f'    ("{word}", "{phonetic}", "{meaning}"),\n')
        f.write("]\n")
    print(f"   ✓ 已保存: {data_file}")
    
    print("\n" + "=" * 60)
    print("完成！")
    print(f"总词汇数: {total_count}")
    print("=" * 60)

if __name__ == "__main__":
    main()
