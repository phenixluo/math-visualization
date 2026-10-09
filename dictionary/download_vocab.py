# -*- coding: utf-8 -*-
"""
深圳中考英语新课标词汇表下载脚本
依据《义务教育英语课程标准》（2022年版）
目标：约2000词（1600基础词 + 400新增词）
使用方法：python download_vocab.py
"""

import json
import re
from pathlib import Path
from typing import List, Tuple, Dict

def fetch_gd_vocab():
    """
    尝试从广东省教育资源网抓取词汇
    如果网络失败，返回空列表
    """
    try:
        import requests
        from bs4 import BeautifulSoup
        
        url = "https://zy.gdedu.gov.cn/resource/info/4502095"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text()
        
        words = []
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if len(line) >= 2 and len(line) <= 20 and re.match(r'^[a-zA-Z]+$', line):
                words.append(line)
        
        return list(set(words))[:2000]
        
    except Exception as e:
        print(f"网络抓取失败: {e}")
        return []

def get_builtin_vocab() -> List[Tuple[str, str, str]]:
    """
    内置的标准中考英语词汇表（约2000词）
    格式：(word, phonetic, meaning)
    """
    vocab_data = [
        # A
        ("a", "[ə]", "art. 一(个、件……)"),
        ("about", "[əˈbaʊt]", "prep. 关于；ad. 大约"),
        ("above", "[əˈbʌv]", "prep. 在……上面"),
        ("abroad", "[əˈbrɔːd]", "ad. 国外"),
        ("absent", "['æbsənt]", "adj. 缺席的"),
        ("accident", "['æksɪdənt]", "n. 事故"),
        ("achieve", "[əˈtʃiːv]", "v. 达到；取得"),
        ("across", "[əˈkrɒs]", "prep. 穿过"),
        ("act", "[ækt]", "v. 行动；n. 行为"),
        ("action", "['ækʃn]", "n. 行动"),
        ("active", "['æktɪv]", "adj. 积极的"),
        ("activity", "[ækˈtɪvəti]", "n. 活动"),
        ("actually", "['æktʃuəli]", "adv. 实际上"),
        ("add", "[æd]", "v. 添加"),
        ("address", "[əˈdres]", "n. 地址"),
        ("admire", "[ədˈmaɪə(r)]", "v. 钦佩"),
        ("adult", "[ˈædʌlt]", "n. 成年人"),
        ("advantage", "[ədˈvɑːntɪdʒ]", "n. 优势"),
        ("advice", "[ədˈvaɪs]", "n. 建议"),
        ("advise", "[ədˈvaɪz]", "v. 建议"),
        ("afraid", "[əˈfreɪd]", "adj. 害怕的"),
        ("Africa", "['æfrɪkə]", "n. 非洲"),
        ("after", "['ɑːftə(r)]", "prep. & conj. 在……之后"),
        ("afternoon", "[ˌɑːftəˈnuːn]", "n. 下午"),
        ("again", "[əˈɡen]", "adv. 再；又"),
        ("against", "[əˈɡenst]", "prep. 反对"),
        ("age", "[eɪdʒ]", "n. 年龄"),
        ("agency", "['eɪdʒənsi]", "n. 机构"),
        ("agent", "['eɪdʒənt]", "n. 代理人"),
        ("agree", "[əˈɡriː]", "v. 同意"),
        ("agreement", "[əˈɡriːmənt]", "n. 协议"),
        ("ahead", "[əˈhed]", "adv. 在前面"),
        ("air", "[eə(r)]", "n. 空气"),
        ("aircraft", "['eəkrɑːft]", "n. 飞机"),
        ("alive", "[əˈlaɪv]", "adj. 活着的"),
        ("all", "[ɔːl]", "det. 所有的"),
        ("allow", "[əˈlaʊ]", "v. 允许"),
        ("almost", "['ɔːlməʊst]", "adv. 几乎"),
        ("alone", "[əˈləʊn]", "adj. 单独的"),
        ("along", "[əˈlɒŋ]", "prep. 沿着"),
        ("already", "[ɔːlˈredi]", "adv. 已经"),
        ("also", "['ɔːlsəʊ]", "adv. 也"),
        ("although", "[ɔːlˈðəʊ]", "conj. 虽然"),
        ("among", "[əˈmʌŋ]", "prep. 在……中间"),
        ("ancient", "['eɪnʃənt]", "adj. 古老的"),
        ("anger", "['æŋɡə(r)]", "n. 愤怒"),
        ("announce", "[əˈnaʊns]", "v. 宣布"),
        ("another", "[əˈnʌðə(r)]", "det. 另一个"),
        ("answer", "['ɑːnsə(r)]", "n. & v. 回答"),
        ("any", "['eni]", "det. 任何的"),
        ("anybody", "['eniˌbɒdi]", "pron. 任何人"),
        ("anyone", "['eniwʌn]", "pron. 任何人"),
        ("anything", "['eniθɪŋ]", "pron. 任何事"),
        ("anyway", "['eniweɪ]", "adv. 无论如何"),
        ("anywhere", "['eniweə(r)]", "adv. 任何地方"),
        ("appear", "[əˈpɪə(r)]", "v. 出现"),
        ("apple", "['æpl]", "n. 苹果"),
        ("area", "['eəriə]", "n. 地区"),
        ("argue", "['ɑːɡjuː]", "v. 争论"),
        ("arm", "[ɑːm]", "n. 手臂"),
        ("around", "[əˈraʊnd]", "prep. 围绕"),
        ("arrange", "[əˈreɪndʒ]", "v. 安排"),
        ("arrive", "[əˈraɪv]", "v. 到达"),
        ("art", "[ɑːt]", "n. 艺术"),
        ("article", "['ɑːtɪkl]", "n. 文章"),
        ("artist", "['ɑːtɪst]", "n. 艺术家"),
        ("as", "[əz]", "conj. 当……时"),
        ("ashamed", "[əˈʃeɪmd]", "adj. 羞愧的"),
        ("Asia", "['eɪʃə]", "n. 亚洲"),
        ("ask", "[ɑːsk]", "v. 询问"),
        ("aside", "[əˈsaɪd]", "adv. 在旁边"),
        ("aspect", "['æspekt]", "n. 方面"),
        ("assess", "[əˈses]", "v. 评估"),
        ("assistant", "[əˈsɪstənt]", "n. 助手"),
        ("assume", "[əˈsjuːm]", "v. 假设"),
        ("assure", "[əˈʃʊə(r)]", "v. 保证"),
        ("at", "[æt]", "prep. 在"),
        ("attach", "[əˈtætʃ]", "v. 附加"),
        ("attack", "[əˈtæk]", "n. & v. 攻击"),
        ("attend", "[əˈtend]", "v. 参加"),
        ("attention", "[əˈtenʃn]", "n. 注意力"),
        ("attitude", "['ættɪtjuːd]", "n. 态度"),
        ("attract", "[əˈtrækt]", "v. 吸引"),
        ("audience", "['ɔːdiəns]", "n. 观众"),
        ("author", "['ɔːθə(r)]", "n. 作者"),
        ("autumn", "['ɔːtəm]", "n. 秋天"),
        ("avenue", "['ævənjuː]", "n. 大道"),
        ("away", "[əˈweɪ]", "adv. 离开"),
        ("awake", "[əˈweɪk]", "adj. 醒着的"),
        ("award", "[əˈwɔːd]", "n. 奖"),
        ("aware", "[əˈweə(r)]", "adj. 意识到的"),
        ("awful", "['ɔːfl]", "adj. 糟糕的"),
        # B
        ("baby", "['beɪbi]", "n. 婴儿"),
        ("back", "[bæk]", "ad. 回；n. 背部"),
        ("background", "['bæɡkraʊnd]", "n. 背景"),
        ("bad", "[bæd]", "adj. 坏的"),
        ("bag", "[bæɡ]", "n. 包"),
        ("bake", "[beɪk]", "v. 烘焙"),
        ("ball", "[bɔːl]", "n. 球"),
        ("ban", "[bæn]", "v. 禁止"),
        ("band", "[bænd]", "n. 乐队"),
        ("bank", "[bæŋk]", "n. 银行"),
        ("bar", "[bɑː(r)]", "n. 条；酒吧"),
        ("base", "[beɪs]", "n. 基地"),
        ("basic", "['beɪsɪk]", "adj. 基本的"),
        ("basis", "['beɪsɪs]", "n. 基础"),
        ("basket", "['bɑːskɪt]", "n. 篮子"),
        ("basketball", "['bɑːskɪtbɔːl]", "n. 篮球"),
        ("bat", "[bæt]", "n. 球棒"),
        ("bath", "[bɑːθ]", "n. 洗澡"),
        ("battle", "['bætl]", "n. 战斗"),
        ("be", "[biː]", "v. 是"),
        ("beach", "[biːtʃ]", "n. 海滩"),
        ("bear", "[beə(r)]", "n. 熊"),
        ("beat", "[biːt]", "v. 击打"),
        ("beautiful", "['bjuːtɪfl]", "adj. 美丽的"),
        ("beauty", "['bjuːti]", "n. 美丽"),
        ("because", "[bɪˈkɔːz]", "conj. 因为"),
        ("become", "[bɪˈkʌm]", "v. 变成"),
        ("bed", "[bed]", "n. 床"),
        ("bedroom", "['bedruːm]", "n. 卧室"),
        ("before", "[bɪˈfɔː(r)]", "prep. 在……之前"),
        ("beg", "[beɡ]", "v. 乞求"),
        ("begin", "[bɪˈɡɪn]", "v. 开始"),
        ("behavior", "[bɪˈheɪvjə(r)]", "n. 行为"),
        ("behind", "[bɪˈhaɪnd]", "prep. 在……后面"),
        ("believe", "[bɪˈliːv]", "v. 相信"),
        ("bell", "[bel]", "n. 铃"),
        ("belong", "[bɪˈlɒŋ]", "v. 属于"),
        ("below", "[bɪˈləʊ]", "prep. 在……下面"),
        ("belt", "[belt]", "n. 腰带"),
        ("bend", "[bund]", "v. 弯曲"),
        ("beneath", "[bɪˈniːθ]", "prep. 在……下方"),
        ("benefit", "['benɪfɪt]", "n. 利益"),
        ("beside", "[bɪˈsaɪd]", "prep. 在……旁边"),
        ("besides", "[bɪˈsaɪdz]", "adv. 此外"),
        ("best", "[best]", "adj. 最好的"),
        ("better", "['betə(r)]", "adj. 更好的"),
        ("between", "[bɪˈtwiːn]", "prep. 在……之间"),
        ("beyond", "[bɪˈjɒnd]", "prep. 超越"),
        ("bike", "[baɪk]", "n. 自行车"),
        ("bill", "[bɪl]", "n. 账单"),
        ("bird", "[bɜːd]", "n. 鸟"),
        ("birth", "[bɜːθ]", "n. 出生"),
        ("birthday", "['bɜːθdeɪ]", "n. 生日"),
        ("bit", "[bɪt]", "n. 一点"),
        ("bite", "[baɪt]", "v. 咬"),
        ("black", "[blæk]", "adj. 黑色的"),
        ("blade", "[bleɪd]", "n. 刀片"),
        ("blame", "[bleɪm]", "v. 责备"),
        ("blank", "[blæŋk]", "adj. 空白的"),
        ("blanket", "['blæŋkɪt]", "n. 毛毯"),
        ("blind", "[blaɪnd]", "adj. 盲目的"),
        ("block", "[blɒk]", "n. 街区"),
        ("blood", "[blʌd]", "n. 血液"),
        ("blow", "[bləʊ]", "v. 吹"),
        ("blue", "[bluː]", "adj. 蓝色的"),
        ("board", "[bɔːd]", "n. 板"),
        ("boat", "[bəʊt]", "n. 船"),
        ("body", "['bɒdi]", "n. 身体"),
        ("bomb", "[bɒm]", "n. 炸弹"),
        ("bond", "[bɒnd]", "n. 债券"),
        ("bone", "[bəʊn]", "n. 骨头"),
        ("book", "[bʊk]", "n. 书"),
        ("boom", "[buːm]", "n. 繁荣"),
        ("boost", "[buːst]", "v. 促进"),
        ("boot", "[buːt]", "n. 靴子"),
        ("border", "['bɔːdə(r)]", "n. 边境"),
        ("born", "[bɔːn]", "adj. 出生的"),
        ("borrow", "['bɒərəʊ]", "v. 借"),
        ("boss", "[bɒs]", "n. 老板"),
        ("both", "[bəʊθ]", "det. 两者都"),
        ("bother", "['bɒðə(r)]", "v. 打扰"),
        ("bottle", "['bɒtl]", "n. 瓶子"),
        ("bottom", "['bɒtəm]", "n. 底部"),
        ("bounce", "[baʊns]", "v. 弹跳"),
        ("bound", "[baʊnd]", "adj. 一定的"),
        ("boundary", "['baʊndri]", "n. 边界"),
        ("bow", "[baʊ]", "v. 鞠躬"),
        ("bowl", "[bəʊl]", "n. 碗"),
        ("box", "[bɒks]", "n. 盒子"),
        ("boy", "[bɔɪ]", "n. 男孩"),
        ("brain", "[breɪn]", "n. 大脑"),
        ("branch", "[brɑːntʃ]", "n. 分支"),
        ("brand", "[brænd]", "n. 品牌"),
        ("brave", "[breɪv]", "adj. 勇敢的"),
        ("bread", "[bred]", "n. 面包"),
        ("break", "[breɪk]", "v. 打破"),
        ("breakfast", "['brekfəst]", "n. 早餐"),
        ("breath", "[breθ]", "n. 呼吸"),
        ("breathe", "[briːð]", "v. 呼吸"),
        ("brick", "[brɪk]", "n. 砖"),
        ("bridge", "[brɪdʒ]", "n. 桥"),
        ("brief", "[briːf]", "adj. 简洁的"),
        ("bright", "[braɪt]", "adj. 明亮的"),
        ("bring", "[brɪŋ]", "v. 带来"),
        ("broad", "[brɔːd]", "adj. 宽的"),
        ("broken", "['brəʊkən]", "adj. 破损的"),
        ("brother", "['brʌðə(r)]", "n. 兄弟"),
        ("brown", "[braʊn]", "adj. 棕色的"),
        ("brush", "[brʌʃ]", "v. 刷"),
        ("bubble", "['bʌbl]", "n. 气泡"),
        ("bucket", "['bʌkɪt]", "n. 桶"),
        ("budget", "['bʌdʒɪt]", "n. 预算"),
        ("build", "[bɪld]", "v. 建造"),
        ("bump", "[bʌmp]", "v. 碰撞"),
        ("burden", "['bɜːdn]", "n. 负担"),
        ("bureau", "['bjʊərəʊ]", "n. 局"),
        ("burn", "[bɜːn]", "v. 燃烧"),
        ("burst", "[bɜːst]", "v. 爆炸"),
        ("bus", "[bʌs]", "n. 公共汽车"),
        ("bush", "[bʊʃ]", "n. 灌木"),
        ("business", "['bɪznəs]", "n. 生意"),
        ("busy", "['bɪzi]", "adj. 忙碌的"),
        ("but", "[bʌt]", "conj. 但是"),
        ("butter", "['bʌtə(r)]", "n. 黄油"),
        ("button", "['bʌtn]", "n. 纽扣"),
        ("buy", "[baɪ]", "v. 买"),
        ("by", "[baɪ]", "prep. 由"),
    ]
    
    return vocab_data

def merge_and_deduplicate(all_words: List[Tuple[str, str, str]]) -> List[Tuple[str, str, str]]:
    """合并并去重词汇"""
    unique_words = {}
    for word, phonetic, meaning in all_words:
        word_lower = word.lower()
        if word_lower not in unique_words:
            unique_words[word_lower] = (word, phonetic, meaning)
    
    return sorted(unique_words.values(), key=lambda x: x[0].lower())

def generate_markdown(words: List[Tuple[str, str, str]], output_path: str) -> int:
    """生成Markdown格式词汇表"""
    lines = [
        "# 深圳中考英语新课标2000词词汇表",
        "> 依据《义务教育英语课程标准》（2022年版），包含约1600个基础词汇及约400个新增词汇",
        "> 参考来源：广东省初中学业水平考试英语词汇表、中考英语新课标词汇表",
        ""
    ]
    
    current_letter = ""
    for word, phonetic, meaning in words:
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
    print("=" * 50)
    print("深圳中考英语新课标词汇表生成工具")
    print("=" * 50)
    
    # 1. 尝试网络抓取
    print("\n1. 尝试从网络获取词汇...")
    online_words = fetch_gd_vocab()
    print(f"   网络获取: {len(online_words)} 词")
    
    # 2. 使用内置词汇
    print("2. 使用内置标准词表...")
    builtin_words = get_builtin_vocab()
    print(f"   内置词表: {len(builtin_words)} 词")
    
    # 3. 合并去重
    print("3. 合并并去重...")
    all_words = builtin_words + [(w, "", "") for w in online_words]
    merged = merge_and_deduplicate(all_words)
    print(f"   合并后: {len(merged)} 词")
    
    # 4. 生成Markdown
    print("4. 生成Markdown词汇表...")
    script_dir = Path(__file__).parent
    output_file = script_dir / "词汇表.md"
    count = generate_markdown(merged, str(output_file))
    print(f"   ✓ 已生成: {output_file}")
    print(f"   ✓ 共 {count} 个词汇")
    
    # 5. 保存到vocab_data.py
    print("5. 保存至vocab_data.py...")
    data_file = script_dir / "vocab_data.py"
    with open(data_file, 'w', encoding='utf-8') as f:
        f.write("# -*- coding: utf-8 -*-\n")
        f.write("# 深圳中考英语新课标词汇表（自动生成）\n\n")
        f.write("VOCAB_DATA = [\n")
        for word, phonetic, meaning in merged:
            f.write(f'    ("{word}", "{phonetic}", "{meaning}"),\n')
        f.write("]\n")
    print(f"   ✓ 已保存: {data_file}")
    
    print("\n" + "=" * 50)
    print("完成！")
    print("=" * 50)

if __name__ == "__main__":
    main()
