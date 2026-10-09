# -*- coding: utf-8 -*-
"""
解析广东省中考英语词汇表HTML并对比合并
"""

import re
import json
from pathlib import Path
from typing import List, Tuple

def parse_vocab_html(html_file: Path) -> List[Tuple[str, str, str]]:
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
    
    # 查找所有表格行
    tables = soup.find_all('table')
    
    for table in tables:
        rows = table.find_all('tr')
        
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
                    if word and re.match(r'^[a-zA-Z]+$', word):
                        words.append((word, phonetic, meaning))
                except:
                    continue
    
    return words

def read_existing_md(md_file: Path) -> Tuple[set, str]:
    """读取现有Markdown词汇表"""
    existing_words = set()
    content = ""
    
    if md_file.exists():
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取所有词汇
        pattern = r'- \*\*([a-zA-Z]+)\*\*'
        matches = re.findall(pattern, content)
        existing_words = set(matches)
    
    return existing_words, content

def generate_markdown(words: List[Tuple[str, str, str]], output_path: Path):
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
    print("广东省中考英语词汇表解析与合并工具")
    print("=" * 60)
    
    script_dir = Path(__file__).parent
    
    # 1. 从HTML提取词汇
    print("\n1. 解析广东省中考英语词汇表HTML...")
    html_file = script_dir / "广东省中考英语词汇表.html"
    
    if not html_file.exists():
        print(f"   ✗ 找不到HTML文件: {html_file}")
        print("   请先运行: python download_gd_vocab_page.py")
        return
    
    gd_words = parse_vocab_html(html_file)
    print(f"   ✓ 提取到 {len(gd_words)} 个词汇")
    
    # 2. 去重
    unique_words = {}
    for word, phonetic, meaning in gd_words:
        word_lower = word.lower()
        if word_lower not in unique_words:
            unique_words[word_lower] = (word, phonetic, meaning)
    
    gd_words = list(unique_words.values())
    print(f"   ✓ 去重后: {len(gd_words)} 个词汇")
    
    # 3. 读取现有词汇表
    print("\n2. 读取现有词汇表...")
    md_file = script_dir / "词汇表.md"
    existing_words, existing_content = read_existing_md(md_file)
    print(f"   ✓ 现有词汇表有 {len(existing_words)} 个词汇")
    
    # 4. 对比分析
    print("\n3. 对比分析...")
    existing_set = set(w.lower() for w, _, _ in gd_words)
    missing_words = [(w, p, m) for w, p, m in gd_words if w.lower() not in existing_words]
    
    print(f"   广东省考纲词汇: {len(gd_words)} 词")
    print(f"   现有词汇表: {len(existing_words)} 词")
    print(f"   缺失词汇: {len(missing_words)} 词")
    
    # 5. 合并并生成
    print("\n4. 合并并生成新词汇表...")
    total_count = generate_markdown(gd_words, md_file)
    print(f"   ✓ 已更新: {md_file}")
    print(f"   ✓ 总词汇数: {total_count}")
    
    # 6. 保存到vocab_data.py
    print("\n5. 保存至vocab_data.py...")
    data_file = script_dir / "vocab_data.py"
    with open(data_file, 'w', encoding='utf-8') as f:
        f.write("# -*- coding: utf-8 -*-\n")
        f.write("# 广东省中考英语词汇表（自动生成）\n\n")
        f.write("VOCAB_DATA = [\n")
        for word, phonetic, meaning in sorted(gd_words, key=lambda x: x[0].lower()):
            f.write(f'    ("{word}", "{phonetic}", "{meaning}"),\n')
        f.write("]\n")
    print(f"   ✓ 已保存: {data_file}")
    
    # 7. 保存JSON备份
    print("\n6. 保存JSON备份...")
    json_file = script_dir / "gd_vocab_list.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump([{"word": w, "phonetic": p, "meaning": m} for w, p, m in gd_words],
                  ensure_ascii=False, indent=2, fp=f)
    print(f"   ✓ 已保存: {json_file}")
    
    print("\n" + "=" * 60)
    print("完成！")
    print(f"总词汇数: {total_count}")
    print("=" * 60)
    
    # 显示前20个词汇
    print("\n前20个词汇示例:")
    for i, (word, phonetic, meaning) in enumerate(sorted(gd_words, key=lambda x: x[0].lower())[:20], 1):
        print(f"  {i:2d}. {word:<20} {phonetic:<25} {meaning}")

if __name__ == "__main__":
    main()
