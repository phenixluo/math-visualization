# -*- coding: utf-8 -*-
"""
抓取广东省中考英语完整词汇表（约1600词）
数据来源：广东省教育资源公共服务平台
使用方法: python fetch_full_vocab.py
"""

import re
import requests
from pathlib import Path
from bs4 import BeautifulSoup
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
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 提取所有词汇
        words = []
        
        # 方法1：查找表格数据
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 3:
                    try:
                        word = cells[1].get_text(strip=True)
                        phonetic = cells[2].get_text(strip=True)
                        meaning = cells[3].get_text(strip=True) if len(cells) > 3 else ""
                        
                        if word and re.match(r'^[a-zA-Z]+$', word):
                            words.append((word, phonetic, meaning))
                    except:
                        continue
        
        # 方法2：如果表格解析失败，使用正则提取
        if len(words) < 100:
            text = soup.get_text()
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                # 匹配格式：序号 单词 音标 释义
                match = re.search(r'^\d+\s+([a-zA-Z]+)\s+(\[[^\]]+\])\s+(.+)$', line)
                if match:
                    word = match.group(1)
                    phonetic = match.group(2)
                    meaning = match.group(3)
                    if word not in [w[0] for w in words]:
                        words.append((word, phonetic, meaning))
        
        print(f"抓取到 {len(words)} 个词汇")
        return words
        
    except Exception as e:
        print(f"抓取失败: {e}")
        return []

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
