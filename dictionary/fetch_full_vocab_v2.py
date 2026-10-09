# -*- coding: utf-8 -*-
"""
抓取广东省中考英语完整词汇表（约1600词）
数据来源：广东省教育资源公共服务平台
使用方法: python fetch_full_vocab_v2.py
"""

import re
import requests
from pathlib import Path
from typing import List, Tuple

def fetch_gd_vocab_from_url() -> List[Tuple[str, str, str]]:
    """
    从广东省教育资源网抓取中考英语词汇表
    返回格式：[(word, phonetic, meaning), ...]
    """
    url = "https://zy.gdedu.gov.cn/player/data1/transform/2022/2/12/11/32/c17c8dd89b3311eaa85a7efd8b80fdb8/2b66e3b683ee29971608647982213ebb.doc/html4/transform.html"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        text = response.text
        
        words = []
        
        # 使用正则表达式提取词汇
        # 匹配格式：序号 单词 音标 释义
        pattern = r'<td[^>]*>(\d+)</td>\s*<td[^>]*>([a-zA-Z\s&]+?)</td>\s*<td[^>]*>(\[?[^\]]+\]?)</td>\s*<td[^>]*>(.+?)</td>'
        
        matches = re.findall(pattern, text, re.DOTALL)
        
        for match in matches:
            seq_num, word, phonetic, meaning = match
            word = word.strip()
            phonetic = phonetic.strip()
            meaning = meaning.strip()
            
            # 清理词汇
            word = re.sub(r'[^\w\s&]', '', word).strip()
            
            # 只保留有效的英语单词
            if word and re.match(r'^[a-zA-Z]+$', word):
                words.append((word, phonetic, meaning))
        
        print(f"正则提取到 {len(words)} 个词汇")
        
        # 如果正则提取失败，尝试其他方法
        if len(words) < 50:
            words = extract_words_by_lines(text)
        
        return words
        
    except Exception as e:
        print(f"抓取失败: {e}")
        return []

def extract_words_by_lines(text: str) -> List[Tuple[str, str, str]]:
    """
    通过行解析提取词汇
    """
    words = []
    lines = text.split('\n')
    
    for line in lines:
        # 清理HTML标签
        clean_line = re.sub(r'<[^>]+>', ' ', line)
        clean_line = clean_line.strip()
        
        # 匹配词汇行格式
        match = re.search(r'^(\d+)\s+([a-zA-Z]+)\s+(\[[^\]]+\])\s+(.+)$', clean_line)
        if match:
            word = match.group(2)
            phonetic = match.group(3)
            meaning = match.group(4)
            words.append((word, phonetic, meaning))
    
    print(f"行解析提取到 {len(words)} 个词汇")
    return words

def read_existing_md(filepath: Path) -> str:
    """读取现有Markdown文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def generate_markdown(words: List[Tuple[str, str, str]], output_path: Path) -> int:
    """生成Markdown格式词汇表"""
    lines = [
        "# 深圳中考英语新课标2000词词汇表",
        "> 依据《义务教育英语课程标准》（2022年版）",
        "> 包含约1600个广东省中考考纲词汇及约400个新增词汇",
        "> 参考来源：广东省初中学业水平考试英语词汇表",
        ""
    ]
    
    current_letter = ""
    for word, phonetic, meaning in sorted(words, key=lambda x: x[0].lower()):
        first_letter = word[0].upper()
        if first_letter != current_letter:
            current_letter = first_letter
            lines.append(f"## {current_letter}")
            lines.append("")
        lines.append(f"- **{word}** {phonetic}  {meaning}")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    return len(words)

def main():
    print("=" * 60)
    print("广东省中考英语词汇表抓取工具")
    print("=" * 60)
    
    # 1. 抓取词汇
    print("\n1. 从广东省教育资源网抓取词汇...")
    words = fetch_gd_vocab_from_url()
    
    if not words:
        print("   ✗ 抓取失败，请检查网络连接")
        return
    
    print(f"   ✓ 成功抓取 {len(words)} 个词汇")
    
    # 2. 去重
    print("2. 去重处理...")
    unique_words = {}
    for word, phonetic, meaning in words:
        word_lower = word.lower()
        if word_lower not in unique_words:
            unique_words[word_lower] = (word, phonetic, meaning)
    
    words = list(unique_words.values())
    print(f"   ✓ 去重后: {len(words)} 词")
    
    # 3. 生成Markdown
    print("3. 生成Markdown词汇表...")
    script_dir = Path(__file__).parent
    output_file = script_dir / "词汇表.md"
    count = generate_markdown(words, output_file)
    print(f"   ✓ 已生成: {output_file}")
    print(f"   ✓ 共 {count} 个词汇")
    
    # 4. 保存至vocab_data.py
    print("4. 保存至vocab_data.py...")
    data_file = script_dir / "vocab_data.py"
    with open(data_file, 'w', encoding='utf-8') as f:
        f.write("# -*- coding: utf-8 -*-\n")
        f.write("# 广东省中考英语词汇表（自动生成）\n\n")
        f.write("VOCAB_DATA = [\n")
        for word, phonetic, meaning in words:
            f.write(f'    ("{word}", "{phonetic}", "{meaning}"),\n')
        f.write("]\n")
    print(f"   ✓ 已保存: {data_file}")
    
    print("\n" + "=" * 60)
    print("完成！")
    print(f"总词汇数: {len(words)}")
    print("=" * 60)

if __name__ == "__main__":
    main()
