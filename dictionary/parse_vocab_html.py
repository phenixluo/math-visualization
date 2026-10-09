# -*- coding: utf-8 -*-
"""
使用BeautifulSoup解析广东省中考英语词汇表HTML
"""

import re
from pathlib import Path

def parse_vocab_html(html_file: Path):
    """解析HTML文件提取词汇"""
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        print("正在安装BeautifulSoup...")
        import subprocess
        subprocess.run(['pip', 'install', 'beautifulsoup4', '-q'], check=True)
        from bs4 import BeautifulSoup
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    words = []
    
    # 方法1：查找所有表格行
    tables = soup.find_all('table')
    print(f"找到 {len(tables)} 个表格")
    
    for table in tables:
        rows = table.find_all('tr')
        print(f"  表格有 {len(rows)} 行")
        
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 3:
                try:
                    seq = cells[0].get_text(strip=True)
                    word = cells[1].get_text(strip=True)
                    phonetic = cells[2].get_text(strip=True)
                    meaning = cells[3].get_text(strip=True) if len(cells) > 3 else ""
                    
                    # 清理文本
                    word = re.sub(r'\s+', ' ', word).strip()
                    phonetic = re.sub(r'\s+', ' ', phonetic).strip()
                    meaning = re.sub(r'\s+', ' ', meaning).strip()
                    
                    # 只保留有效的英语单词
                    if word and re.match(r'^[a-zA-Z]+$|^[a-zA-Z]+\([a-zA-Z]+\)$', word):
                        # 处理括号中的同义词，如 a(an)
                        clean_word = re.sub(r'\(.*?\)', '', word).strip()
                        if clean_word:
                            words.append((clean_word, phonetic, meaning))
                except Exception as e:
                    continue
    
    print(f"\n从表格提取到 {len(words)} 个词汇")
    
    # 方法2：如果表格提取失败，尝试其他方式
    if len(words) < 100:
        print("尝试其他提取方式...")
        # 查找所有包含音标模式的文本
        text = soup.get_text()
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

def main():
    script_dir = Path(__file__).parent
    html_file = script_dir / "广东省中考英语词汇表.html"
    
    if not html_file.exists():
        print(f"找不到HTML文件: {html_file}")
        return
    
    print("=" * 60)
    print("解析广东省中考英语词汇表")
    print("=" * 60)
    
    words = parse_vocab_html(html_file)
    
    # 去重
    unique_words = {}
    for word, phonetic, meaning in words:
        word_lower = word.lower()
        if word_lower not in unique_words:
            unique_words[word_lower] = (word, phonetic, meaning)
    
    words = list(unique_words.values())
    print(f"\n去重后: {len(words)} 个词汇")
    
    # 保存为JSON方便查看
    import json
    json_file = script_dir / "gd_vocab_list.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump([{"word": w, "phonetic": p, "meaning": m} for w, p, m in words], 
                  ensure_ascii=False, indent=2)
    print(f"已保存到: {json_file}")
    
    # 显示前20个词汇
    print("\n前20个词汇示例:")
    for i, (word, phonetic, meaning) in enumerate(words[:20], 1):
        print(f"  {i}. {word} {phonetic}  {meaning}")

if __name__ == "__main__":
    main()
