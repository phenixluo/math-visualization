# -*- coding: utf-8 -*-
"""
抓取并处理新课标新增词汇
数据来源：学科网 义务教育课程标准(2022年版)英语新增词汇
使用方法: python fetch_new_vocab.py
"""

import re
import json
from pathlib import Path
from typing import List, Tuple

def extract_new_vocab_from_text() -> List[Tuple[str, str, str]]:
    """
    从搜索结果中提取的新课标新增词汇
    根据构词法推导出的部分名词、形容词、副词等不计入
    """
    # A段新增词汇
    new_vocab_a = [
        ("account", "[ə'kaʊnt]", "n.账户；账目 v.认为是"),
        ("ache", "[eɪk]", "v.&n.疼痛"),
        ("ad", "[əd]", "n.广告 (=advertisement)"),
        ("admire", "[əd'maɪə(r)]", "v.钦佩；羡慕"),
        ("adult", "[ə'dʌlt]", "n.成年人"),
        ("ahead", "[ə'hed]", "adv.在前面；向前"),
        ("AI", "[ˌeɪ'aɪ]", "n.人工智能 (=artificial intelligence)"),
        ("aid", "[eɪd]", "n.&v.帮助；援助"),
        ("aim", "[eɪm]", "n.目标；目的 v.瞄准；旨在"),
        ("alarm", "[ə'lɑːm]", "n.警报 v.警告"),
        ("amazing", "[ə'meɪzɪŋ]", "adj.令人惊叹的"),
        ("apartment", "[ə'pɑːtmənt]", "n.公寓"),
        ("app", "[æp]", "n.应用程序 (=application)"),
        ("argue", "['ɑːɡjuː]", "v.争论；争吵"),
        ("astronaut", "['æstrənɔːt]", "n.宇航员"),
        ("athlete", "['æθliːt]", "n.运动员"),
        ("attack", "[ə'tæk]", "n.&v.袭击；攻击"),
        ("average", "['ævərɪdʒ]", "n.平均数 adj.平均的"),
        ("award", "[ə'wɔːd]", "n.奖品；奖项 v.授予"),
        ("aware", "[ə'weə(r)]", "adj.意识到的；明白的"),
    ]
    
    # B段新增词汇
    new_vocab_b = [
        ("badminton", "['bædmɪntən]", "n.羽毛球"),
        ("balance", "['bæləns]", "n.&v.平衡"),
        ("band", "[bænd]", "n.乐队；带子"),
        ("bat", "[bæt]", "n.球拍；蝙蝠"),
        ("bath", "[bɑːθ]", "n.洗澡；浴室"),
        ("bee", "[biː]", "n.蜜蜂"),
        ("behave", "[bɪ'heɪv]", "v.表现；行为"),
        ("belong", "[bɪ'lɒŋ]", "v.属于"),
        ("belt", "[belt]", "n.腰带；皮带"),
        ("benefit", "['benɪfɪt]", "n.好处；益处 v.受益"),
        ("biology", "[baɪ'ɒlədʒi]", "n.生物学"),
        ("bleed", "[bliːd]", "v.流血"),
        ("boil", "[bɔɪl]", "v.煮沸"),
        ("breath", "[breθ]", "n.呼吸；一口气"),
        ("budget", "['bʌdʒɪt]", "n.预算"),
        ("bully", "['bʊli]", "n.霸凌者 v.欺凌"),
        ("butter", "['bʌtə(r)]", "n.黄油"),
        ("butterfly", "['bʌtəflaɪ]", "n.蝴蝶"),
        ("cabbage", "['kæbɪdʒ]", "n.卷心菜"),
        ("calm", "[kɑːm]", "adj.镇静的 v.使平静"),
        ("cancer", "['kænsə(r)]", "n.癌症"),
        ("case", "[keɪs]", "n.情况；案例"),
        ("cash", "[kæʃ]", "n.现金"),
        ("challenge", "['tʃælɪndʒ]", "n.&v.挑战"),
        ("champion", "['tʃæmpɪən]", "n.冠军"),
        ("character", "['kærəktə(r)]", "n.角色；性格"),
        ("charity", "['tʃærəti]", "n.慈善；慈善机构"),
        ("chat", "[tʃæt]", "n.&v.聊天"),
        ("cheat", "[tʃiːt]", "v.欺骗；作弊"),
        ("cheese", "[tʃiːz]", "n.奶酪"),
        ("chip", "[tʃɪp]", "n.芯片；炸薯条"),
        ("citizen", "['sɪtɪzn]", "n.公民；市民"),
        ("classic", "['klæsɪk]", "adj.经典的 n.名著"),
        ("click", "[klɪk]", "v.&n.点击"),
        ("climate", "['klaɪmət]", "n.气候"),
        ("company", "['kʌmpəni]", "n.公司；陪伴"),
    ]
    
    # C段新增词汇
    new_vocab_c = [
        ("compete", "[kəm'piːt]", "v.竞争；比赛"),
        ("confidence", "['kɒnfɪdəns]", "n.自信"),
        ("congratulation", "[kənˌɡrætʃʊ'leɪʃn]", "n.祝贺"),
        ("convenient", "[kən'viːniənt]", "adj.方便的"),
        ("cooperate", "[kəʊ'ɒpəreɪt]", "v.合作"),
        ("creative", "[kriː'eɪtɪv]", "adj.创造性的"),
        ("crowded", "['kraʊdɪd]", "adj.拥挤的"),
        ("cucumber", "['kjuːkʌmbə(r)]", "n.黄瓜"),
        ("curious", "['kjʊəriəs]", "adj.好奇的"),
    ]
    
    # D段新增词汇
    new_vocab_d = [
        ("death", "[deθ]", "n.死亡"),
        ("dentist", "['dentɪst]", "n.牙医"),
        ("design", "[dɪ'zaɪn]", "n.&v.设计"),
        ("diet", "['daɪət]", "n.饮食"),
        ("digital", "['dɪdʒɪtl]", "adj.数字的"),
        ("disappoint", "[ˌdɪsə'pɔɪnt]", "v.使失望"),
        ("disaster", "[dɪ'zɑːstə(r)]", "n.灾难"),
        ("disease", "[dɪ'ziːz]", "n.疾病"),
        ("doll", "[dɒl]", "n.玩偶"),
        ("donate", "[dəʊ'neɪt]", "v.捐赠"),
        ("download", "[ˌdaʊn'ləʊd]", "v.&n.下载"),
        ("drama", "['drɑːmə]", "n.戏剧"),
        ("duty", "['djuːti]", "n.责任；义务"),
    ]
    
    # E段新增词汇
    new_vocab_e = [
        ("eagle", "['iːɡl]", "n.鹰"),
        ("effect", "[ɪ'fekt]", "n.影响；效果"),
        ("effort", "['efət]", "n.努力"),
        ("electric", "[ɪ'lektrɪk]", "adj.电的"),
        ("emergency", "[ɪ'mɜːdʒənsi]", "n.紧急情况"),
        ("energy", "['enədʒi]", "n.能量；精力"),
        ("era", "['ɪərə]", "n.时代；年代"),
        ("event", "[ɪ'vent]", "n.事件"),
        ("expert", "['ekspɜːt]", "n.专家"),
        ("explore", "[ɪk'splɔː(r)]", "v.探索"),
    ]
    
    # F段新增词汇
    new_vocab_f = [
        ("false", "[fɔːls]", "adj.错误的"),
        ("familiar", "[fə'mɪliə(r)]", "adj.熟悉的"),
        ("fashion", "['fæʃn]", "n.时尚；时装"),
        ("final", "['faɪnl]", "adj.最后的 n.决赛"),
        ("fireman", "['faɪəmən]", "n.消防员"),
        ("flat", "[flæt]", "n.公寓 adj.平的"),
        ("flood", "[flʌd]", "n.洪水 v.淹没"),
        ("focus", "['fəʊkəs]", "v.&n.聚焦；集中"),
        ("folk", "[fəʊk]", "n.民间音乐 adj.民间的"),
        ("fool", "[fuːl]", "n.傻瓜 v.欺骗"),
        ("forever", "[fɔː'revə(r)]", "adv.永远"),
        ("found", "[faʊnd]", "v.建立（find的过去式）"),
        ("freeze", "[friːz]", "v.结冰；冻结"),
    ]
    
    # G-H段新增词汇
    new_vocab_gh = [
        ("gas", "[ɡæs]", "n.气体；汽油"),
        ("goal", "[ɡəʊl]", "n.目标；球门"),
        ("graduate", "['ɡrædʒuət]", "v.毕业 n.毕业生"),
        ("greet", "[ɡriːt]", "v.问候；迎接"),
        ("gym", "[dʒɪm]", "n.体育馆"),
        ("harm", "[hɑːm]", "n.&v.伤害"),
        ("hike", "[haɪk]", "v.&n.远足"),
        ("honey", "['hʌni]", "n.蜂蜜；亲爱的"),
        ("honour", "['onə(r)]", "n.荣誉 v.尊敬"),
        ("host", "[həʊst]", "n.主人 v.主办"),
        ("humour", "['hjuːmə(r)]", "n.幽默"),
        ("hunt", "[hʌnt]", "v.&n.狩猎；寻找"),
    ]
    
    # I-J段新增词汇
    new_vocab_ij = [
        ("improve", "[ɪm'pruːv]", "v.改善；提高"),
        ("insect", "['ɪnsekt]", "n.昆虫"),
        ("jeans", "[dʒiːnz]", "n.牛仔裤"),
        ("jog", "[dʒɒɡ]", "v.&n.慢跑"),
        ("joy", "[dʒɔɪ]", "n.快乐；喜悦"),
        ("judge", "[dʒʌdʒ]", "n.法官 v.判断"),
        ("junior", "['dʒuːniə(r)]", "adj.较年轻的 n.年轻人"),
    ]
    
    # K-L段新增词汇
    new_vocab_kl = [
        ("lamp", "[læmp]", "n.灯"),
        ("landscape", "['lændskeɪp]", "n.风景；地形"),
        ("lantern", "['læntən]", "n.灯笼"),
        ("laptop", "['læptɒp]", "n.笔记本电脑"),
        ("lawyer", "['lɔːjə(r)]", "n.律师"),
        ("likely", "['laɪkli]", "adj.可能的 adv.可能"),
        ("literature", "['lɪtrətʃə(r)]", "n.文学"),
        ("loss", "[lɒs]", "n.损失；丢失"),
    ]
    
    # M段新增词汇
    new_vocab_m = [
        ("madam", "['mædəm]", "n.女士"),
        ("mall", "[mɔːl]", "n.购物中心"),
        ("manner", "['mænə(r)]", "n.礼貌；方式"),
        ("material", "[mə'tɪəriəl]", "n.材料 adj.物质的"),
        ("medal", "['medl]", "n.奖牌"),
        ("medium", "['miːdiəm]", "n.媒介；媒体"),
        ("mirror", "['mɪrə(r)]", "n.镜子"),
        ("moment", "['məʊmənt]", "n.时刻；瞬间"),
        ("mutton", "['mʌtn]", "n.羊肉"),
    ]
    
    # N-O段新增词汇
    new_vocab_no = [
        ("negative", "['neɡətɪv]", "adj.消极的；负面的"),
        ("novel", "['nɒvl]", "n.小说 adj.新的"),
        ("ocean", "['əʊʃn]", "n.海洋"),
        ("onion", "['ʌnjən]", "n.洋葱"),
        ("opera", "['ɒprə]", "n.歌剧"),
        ("operate", "['ɒpəreɪt]", "v.操作；手术"),
        ("opinion", "[ə'pɪnjən]", "n.意见；看法"),
        ("oven", "['ʌvn]", "n.烤箱"),
    ]
    
    # P段新增词汇
    new_vocab_p = [
        ("packet", "['pækɪt]", "n.小包；袋"),
        ("paragraph", "['pærəɡrɑːf]", "n.段落"),
        ("partner", "['pɑːtnə(r)]", "n.伙伴；搭档"),
        ("penguin", "['peŋɡwɪn]", "n.企鹅"),
        ("pepper", "['pepə(r)]", "n.胡椒；辣椒"),
        ("percent", "[pə'sent]", "n.百分之..."),
        ("perform", "[pə'fɔːm]", "v.表演；执行"),
        ("piano", "[pɪ'ænəʊ]", "n.钢琴"),
        ("pill", "[pɪl]", "n.药丸"),
        ("pizza", "['piːtsə]", "n.披萨"),
        ("plastic", "['plæstɪk]", "n.塑料 adj.塑料的"),
        ("plate", "[pleɪt]", "n.盘子"),
        ("poet", "['pəʊɪt]", "n.诗人"),
        ("pork", "[pɔːk]", "n.猪肉"),
        ("position", "[pə'zɪʃn]", "n.位置；职位"),
        ("positive", "['pɒzətɪv]", "adj.积极的；正面的"),
        ("pot", "[pɒt]", "n.锅；壶"),
        ("pour", "[pɔː(r)]", "v.倒； pouring"),
        ("power", "['paʊə(r)]", "n.力量；权力"),
        ("prefer", "[prɪ'fɜː(r)]", "v.更喜欢"),
        ("press", "[pres]", "v.&n.按；压"),
        ("prince", "[prɪns]", "n.王子"),
        ("princess", "[prɪn'ses]", "n.公主"),
        ("prove", "[pruːv]", "v.证明"),
        ("publish", "['pʌblɪʃ]", "v.出版；发表"),
    ]
    
    # Q-R段新增词汇
    new_vocab_qr = [
        ("quality", "['kwɒləti]", "n.质量；品质"),
        ("rainbow", "['reɪnbəʊ]", "n.彩虹"),
        ("rather", "['rɑːðə(r)]", "adv.相当；宁可"),
        ("recommend", "[ˌrekə'mend]", "v.推荐"),
        ("recycle", "[ˌriː'saɪkl]", "v.回收利用"),
        ("reduce", "[rɪ'djuːs]", "v.减少"),
        ("remind", "[rɪ'maɪnd]", "v.提醒"),
        ("respect", "[rɪ'spekt]", "v.&n.尊重"),
        ("responsible", "[rɪ'spɒnsəbl]", "adj.负责任的"),
        ("rocket", "['rɒɪkɪt]", "n.火箭"),
    ]
    
    # S段新增词汇
    new_vocab_s = [
        ("scare", "[skeə(r)]", "v.&n.惊吓"),
        ("shark", "[ʃɑːk]", "n.鲨鱼"),
        ("shelf", "[ʃelf]", "n.架子"),
        ("shock", "[ʃɒk]", "n.&v.震惊"),
        ("shoot", "[ʃuːt]", "v.射击；拍摄"),
        ("ski", "[skiː]", "v.&n.滑雪"),
        ("slim", "[slɪm]", "adj.苗条的"),
        ("snack", "[snæk]", "n.点心；小吃"),
        ("socialism", "['səʊʃəlɪzəm]", "n.社会主义"),
        ("soil", "[sɔɪl]", "n.土壤"),
        ("soldier", "['səʊldʒə(r)]", "n.士兵"),
        ("stage", "[steɪdʒ]", "n.舞台；阶段"),
        ("stress", "[stres]", "n.压力"),
        ("style", "[staɪl]", "n.风格；款式"),
        ("suffer", "['sʌfə(r)]", "v.遭受；忍受"),
        ("suit", "[suːt]", "n.西服 v.适合"),
        ("survive", "[sə'vaɪv]", "v.生存；幸存"),
        ("sweep", "[swiːp]", "v.打扫"),
        ("symbol", "['sɪmbəl]", "n.象征；符号"),
    ]
    
    # T-W-Y段新增词汇
    new_vocab_twy = [
        ("talent", "['tælənt]", "n.天赋；才能"),
        ("tap", "[tæp]", "n.水龙头"),
        ("teamwork", "['tiːmwɜːk]", "n.团队合作"),
        ("teenage", "['tiːnɪdʒ]", "adj.青少年的"),
        ("tent", "[tent]", "n.帐篷"),
        ("therefore", "['ðeəfɔː(r)]", "adv.因此"),
        ("throat", "[θrəʊt]", "n.咽喉"),
        ("thunder", "['θʌndə(r)]", "n.雷"),
        ("tofu", "['təʊfuː]", "n.豆腐"),
        ("uniform", "['juːnɪfɔːm]", "n.制服"),
        ("universe", "['juːnɪvɜːs]", "n.宇宙"),
        ("view", "[vjuː]", "n.看法；视野"),
        ("virus", "['vaɪrəs]", "n.病毒"),
        ("voluntary", "['vɒləntəri]", "adj.自愿的"),
        ("volunteer", "[ˌvɒlən'tɪə(r)]", "n.志愿者 v.志愿做"),
        ("vote", "[vəʊt]", "v.&n.投票"),
        ("wave", "[veɪv]", "n.挥手；波浪"),
        ("whale", "[weɪl]", "n.鲸"),
        ("within", "[wɪ'ðɪn]", "prep.在...之内"),
        ("wolf", "[wʊlf]", "n.狼"),
        ("yogurt", "['jɒɡət]", "n.酸奶"),
        ("youth", "[juːθ]", "n.青年；青春"),
    ]
    
    # 合并所有新增词汇
    all_new_vocab = (
        new_vocab_a + new_vocab_b + new_vocab_c + new_vocab_d + 
        new_vocab_e + new_vocab_f + new_vocab_gh + new_vocab_ij +
        new_vocab_kl + new_vocab_m + new_vocab_no + new_vocab_p +
        new_vocab_qr + new_vocab_s + new_vocab_twy
    )
    
    return all_new_vocab

def read_existing_vocab(md_file: Path) -> set:
    """读取现有词汇表中的词汇"""
    existing_words = set()
    
    if md_file.exists():
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取所有词汇
        pattern = r'- \*\*([a-zA-Z]+)\*\*'
        matches = re.findall(pattern, content)
        existing_words = set(matches)
    
    return existing_words

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
    print("新课标新增词汇抓取与合并工具")
    print("=" * 60)
    
    script_dir = Path(__file__).parent
    
    # 1. 提取新增词汇
    print("\n1. 提取新课标新增词汇...")
    new_vocab = extract_new_vocab_from_text()
    print(f"   ✓ 新增词汇: {len(new_vocab)} 词")
    
    # 2. 读取现有词汇表
    print("\n2. 读取现有词汇表...")
    md_file = script_dir / "词汇表.md"
    existing_words = read_existing_vocab(md_file)
    print(f"   ✓ 现有词汇: {len(existing_words)} 词")
    
    # 3. 找出需要添加的新词汇
    print("\n3. 对比分析...")
    missing_words = []
    for word, phonetic, meaning in new_vocab:
        if word.lower() not in existing_words:
            missing_words.append((word, phonetic, meaning))
    
    print(f"   缺失词汇: {len(missing_words)} 词")
    
    if not missing_words:
        print("   ✓ 所有新增词汇已在词汇表中，无需补充")
        return
    
    # 4. 读取现有完整词汇表
    print("\n4. 读取完整词汇表...")
    html_file = script_dir / "gd_vocab_list.json"
    existing_full_vocab = []
    
    if html_file.exists():
        with open(html_file, 'r', encoding='utf-8') as f:
            existing_full_vocab = json.load(f)
        
        existing_set = set(item['word'].lower() for item in existing_full_vocab)
        
        # 添加新词汇
        for word, phonetic, meaning in missing_words:
            if word.lower() not in existing_set:
                existing_full_vocab.append({
                    'word': word,
                    'phonetic': phonetic,
                    'meaning': meaning
                })
                existing_set.add(word.lower())
    
    # 5. 生成新词汇表
    print("\n5. 生成新词汇表...")
    words_list = [(item['word'], item['phonetic'], item['meaning']) for item in existing_full_vocab]
    total_count = generate_markdown(words_list, md_file)
    print(f"   ✓ 总词汇数: {total_count}")
    
    # 6. 更新vocab_data.py
    print("\n6. 更新vocab_data.py...")
    data_file = script_dir / "vocab_data.py"
    with open(data_file, 'w', encoding='utf-8') as f:
        f.write("# -*- coding: utf-8 -*-\n")
        f.write("# 深圳中考英语新课标词汇表（自动生成）\n\n")
        f.write("VOCAB_DATA = [\n")
        for word, phonetic, meaning in sorted(words_list, key=lambda x: x[0].lower()):
            f.write(f'    ("{word}", "{phonetic}", "{meaning}"),\n')
        f.write("]\n")
    print(f"   ✓ 已保存: {data_file}")
    
    print("\n" + "=" * 60)
    print("完成！")
    print(f"总词汇数: {total_count}")
    print(f"新增词汇: {len(missing_words)} 词")
    print("=" * 60)
    
    # 显示新增词汇示例
    print("\n新增词汇示例（前20个）:")
    for i, (word, phonetic, meaning) in enumerate(sorted(missing_words, key=lambda x: x[0].lower())[:20], 1):
        print(f"  {i:2d}. {word:<20} {phonetic:<25} {meaning}")

if __name__ == "__main__":
    main()
