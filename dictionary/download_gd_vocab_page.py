# -*- coding: utf-8 -*-
"""
下载广东省中考英语词汇表网页并保存
使用方法: python download_gd_vocab_page.py
"""

import requests
from pathlib import Path

def main():
    url = "https://zy.gdedu.gov.cn/player/data1/transform/2022/2/12/11/32/c17c8dd89b3311eaa85a7efd8b80fdb8/2b66e3b683ee29971608647982213ebb.doc/html4/transform.html"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    }
    
    try:
        print("正在下载广东省中考英语词汇表...")
        response = requests.get(url, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        
        # 保存网页
        output_file = Path(__file__).parent / "广东省中考英语词汇表.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print(f"✓ 已保存到: {output_file}")
        print(f"  文件大小: {len(response.text)} 字节")
        
        # 同时保存纯文本版本便于查看
        text_file = Path(__file__).parent / "广东省中考英语词汇表_纯文本.txt"
        # 简单清理HTML标签获取文本
        import re
        text = re.sub(r'<[^>]+>', ' ', response.text)
        text = re.sub(r'\s+', ' ', text)
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(text)
        
        print(f"✓ 已保存纯文本到: {text_file}")
        
    except Exception as e:
        print(f"✗ 下载失败: {e}")

if __name__ == "__main__":
    main()
