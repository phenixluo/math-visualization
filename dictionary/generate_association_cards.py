# -*- coding: utf-8 -*-
"""
生成联想记忆卡片（按词族拓展）
使用方法: python generate_association_cards.py
"""

import re
from pathlib import Path
from typing import List, Tuple, Dict

# 词族联想词典（基于常见词根词缀和扩展）
WORD_FAMILY_DICT = {
    # A开头
    "able": ["unable", "ability", "unable", "enable"],
    "accept": ["acceptable", "acceptance", "accepted", "accepting"],
    "ache": ["headache", "stomachache", "toothache", "backache"],
    "active": ["actively", "activity", "actively", "activation"],
    "advantage": ["disadvantage", "advantaged", "advantageous"],
    "advise": ["advice", "adviser", "advisor", "advisable"],
    "afraid": ["afraid", "frighten", "frightened", "frightening"],
    "agree": ["agreement", "disagree", "disagreement", "agreeable"],
    "allow": ["allowed", "allowing", "allows", "allowance"],
    "amaze": ["amazing", "amazed", "amazement", "amazingly"],
    "anger": ["angry", "angrily", "anger"],
    "ancient": ["anciently", "ancientness"],
    "announce": ["announcement", "announced", "announcing"],
    "anxious": ["anxiously", "anxiety", "anxiousness"],
    "apply": ["application", "applicant", "applied", "applying"],
    "appear": ["appearance", "appeared", "appearing", "disappear"],
    "appoint": ["appointment", "appointed", "appointing"],
    "appreciate": ["appreciation", "appreciated", "appreciable"],
    "argue": ["argument", "argued", "arguing", "arguable"],
    "arm": ["armed", "arms", "army", "armless"],
    "arrange": ["arrangement", "arranged", "arranging"],
    "arrive": ["arrival", "arrived", "arriving"],
    "ask": ["asked", "asking", "asks", "askful"],
    "attack": ["attacked", "attacking", "attacker", "attacks"],
    "attend": ["attendance", "attended", "attending", "attendant"],
    "attention": ["attentive", "attently", "attentiveness"],
    "attract": ["attraction", "attractive", "attracted", "attractively"],
    "awake": ["awaken", "awakening", "awoke", "awoken"],
    "award": ["awarded", "awarding", "awards", "awardless"],
    "aware": ["awareness", "unaware", "unawareness"],
    
    # B开头
    "be": ["being", "been", "beauty", "beautiful", "beautifully"],
    "bear": ["bearing", "bears", "bore", "borne", "bearable"],
    "beat": ["beaten", "beating", "beats", "beauty"],
    "become": ["became", "becoming", "becomes"],
    "begin": ["beginning", "begins", "begun", "beginner"],
    "believe": ["belief", "believed", "believing", "believable", "unbelievable"],
    "belong": ["belonging", "belongings"],
    "big": ["bigger", "biggest", "bigly", "bigness"],
    "bind": ["bound", "binding", "bounds", "bond"],
    "bite": ["bit", "bitten", "biting", "biter"],
    "blame": ["blamed", "blaming", "blames", "blameless"],
    "break": ["broken", "breaking", "breaks", "breakable", "breakfast"],
    "breathe": ["breath", "breathless", "breathing", "breathlessly"],
    "bring": ["brought", "bringing", "brings", "carrier"],
    "build": ["building", "built", "builder", "builds"],
    "burn": ["burned", "burning", "burnt", "burner"],
    "buy": ["bought", "buying", "buys", "buyer"],
    
    # C开头
    "call": ["called", "calling", "calls", "caller"],
    "care": ["cared", "careful", "carefully", "carelessness", "careless"],
    "carry": ["carried", "carrying", "carries", "carrier"],
    "catch": ["caught", "catching", "catches", "catcher"],
    "cause": ["caused", "causing", "causes", "causal", "causation"],
    "celebrate": ["celebration", "celebrated", "celebrating", "celebratory"],
    "change": ["changed", "changing", "changes", "changeable", "changes"],
    "charge": ["charged", "charging", "charges", "charger"],
    "check": ["checked", "checking", "checks", "checker"],
    "choose": ["chose", "chosen", "choosing", "choice", "choicer"],
    "clean": ["cleaned", "cleaning", "cleans", "cleaner", "cleanest", "cleanness"],
    "clear": ["clearly", "clearness", "cleared", "clearing"],
    "close": ["closed", "closing", "closes", "closer", "closest", "closely", "closeness"],
    "collect": ["collected", "collecting", "collector", "collection", "collections"],
    "comfort": ["comfortable", "comfortably", "comforted", "comforting"],
    "compare": ["compared", "comparing", "compares", "comparison", "comparative"],
    "compete": ["competition", "competitive", "competitively", "competitor", "competed", "competing"],
    "complete": ["completed", "completing", "completes", "completely", "completeness", "completion"],
    "consider": ["considered", "considering", "considers", "consideration"],
    "connect": ["connected", "connecting", "connects", "connection", "connections"],
    "contain": ["contained", "containing", "contains", "container", "contents"],
    "continue": ["continued", "continuing", "continues", "continuation", "continuously"],
    "control": ["controlled", "controlling", "controls", "controller", "controllable"],
    "conversation": ["conversational", "converse", "conversed", "conversing"],
    "create": ["created", "creating", "creates", "creation", "creative", "creatively", "creator"],
    "cross": ["crossed", "crossing", "crosses", "crosswise"],
    "cry": ["cried", "crying", "cries", "cryer"],
    
    # D开头
    "decide": ["decided", "deciding", "decides", "decision", "decisive", "decisively"],
    "describe": ["described", "describing", "describes", "description", "descriptive"],
    "develop": ["developed", "developing", "develops", "development", "developer", "developed"],
    "die": ["died", "dying", "dies", "dead", "death", "deadly"],
    "dig": ["dug", "digging", "digs", "digger"],
    "direct": ["directed", "directing", "directs", "direction", "directly", "director", "directory"],
    "disappoint": ["disappointed", "disappointing", "disappointment", "disappointingly"],
    "discover": ["discovered", "discovering", "discovers", "discovery", "discoverer"],
    "discuss": ["discussed", "discussing", "discusses", "discussion"],
    "do": ["did", "done", "doing", "does", "doer"],
    
    # E开头
    "eat": ["ate", "eaten", "eating", "eater", "eats"],
    "educate": ["educated", "educating", "educates", "education", "educational", "educator"],
    "effect": ["effective", "effectively", "effectiveness", "ineffective"],
    "effort": ["effortless", "effortlessly"],
    "elect": ["elected", "electing", "elects", "election", "electoral", "electric", "electricity"],
    "encourage": ["encouraged", "encouraging", "encourages", "encouragement", "encouragingly"],
    "end": ["ended", "ending", "ends", "endless", "endeavor", "emergency"],
    "enjoy": ["enjoyed", "enjoying", "enjoys", "enjoyable", "enjoyment"],
    "enter": ["entered", "entering", "enters", "entrance", "entertainment"],
    "equal": ["equaled", "equaling", "equals", "equality", "equally", "equivalent"],
    "establish": ["established", "establishing", "establishes", "establishment"],
    "exist": ["existed", "existing", "exists", "existence", "existent"],
    "expand": ["expanded", "expanding", "expands", "expansion", "expansive"],
    "expect": ["expected", "expecting", "expects", "expectation", "unexpected"],
    "explore": ["explored", "exploring", "explores", "explorer", "exploration"],
    "express": ["expressed", "expressing", "expresses", "expression", "expressive", "expressly"],
    
    # F开头
    "fail": ["failed", "failing", "fails", "failure", "failures"],
    "fall": ["fell", "fallen", "falling", "falls", "fallen"],
    "feed": ["fed", "feeding", "feeds", " feeder", "food", "fool"],
    "feel": ["felt", "feeling", "feels", "feeler"],
    "fight": ["fought", "fighting", "fights", "fighter", "fighting"],
    "find": ["found", "finding", "finds", "founder", "foundations"],
    "finish": ["finished", "finishing", "finishes", "finisher", "final", "finally", "finale"],
    "fire": ["fired", "filter", "filtering", "filters"],
    "fit": ["fitting", "fitted", "fits", "fitness"],
    "fix": ["fixed", "fixing", "fixes", "fixer", "fixable"],
    "fly": ["flew", "flown", "flying", "flies", "flight", "flyer"],
    "focus": ["focused", "focusing", "focuses", "focusable"],
    "follow": ["followed", "following", "follows", "follower", "followers", "followable"],
    "force": ["forced", "forcing", "forces", "forcible", " forcibly"],
    "forecast": ["forecasted", "forecasting", "forecasts", "forecaster"],
    "forget": ["forgot", "forgotten", "forgetting", "forgettable"],
    "forgive": ["forgave", "forgiven", "forgiving", "forgivable"],
    "form": ["formed", "forming", "forms", "formation", "formal", " formally", "former", "formerly", "format", "formation", "framework"],
    "found": ["founded", "founding", "founder", "foundation", "foundations"],
    "freeze": ["froze", "frozen", "freezing", "freezer"],
    
    # G开头
    "gather": ["gathered", "gathering", "gathers", "gathering"],
    "give": ["gave", "given", "giving", "giver", "gifts"],
    "go": ["went", "gone", "going", "goes", "going"],
    "grab": ["grabbed", "grabbing", "grabs", "grabber"],
    "grow": ["grew", "grown", "growing", "grows", "growth", "grower"],
    
    # H开头
    "hang": ["hung", "hanging", "hangs", "hanger"],
    "happen": ["happened", "happening", "happens", "happening"],
    "have": ["had", "having", "has", "having"],
    "hear": ["heard", "hearing", "hears", "hearer"],
    "heat": ["heated", "heating", "heats", "heater", "heatable"],
    "help": ["helped", "helping", "helps", "helper", "helpful", "helpfully", "helpfulness", "helpless"],
    "hide": ["hid", "hidden", "hiding", "hides"],
    "hold": ["held", "holding", "holds", "holder", "holdable"],
    "happen": ["happened", "happening", "happens", "happenings"],
    
    # I开头
    "imagine": ["imagined", "imagining", "imagines", "imagination", "imaginable", "imaginative"],
    "improve": ["improved", "improving", "improves", "improvement", "improvements", "improvable"],
    "include": ["included", "including", "includes", "inclusion", "inclusive"],
    "increase": ["increased", "increasing", "increases", "increasingly", "increaseable"],
    "industrious": ["industriousness", "industry", "industrial"],
    
    # J开头
    "join": ["joined", "joining", "joins", "joiner", "joint", "jointly"],
    "judge": ["judged", "judging", "judges", "judgment", "judgeable"],
    
    # K开头
    "keep": ["kept", "keeping", "keeps", "keeper", "keepsake"],
    "kick": ["kicked", "kicking", "kicks", "kicker"],
    "kill": ["killed", "killing", "kills", "killer", "killable"],
    "know": ["knew", "known", "knowing", "knows", "knowledge", "knowledgeable", "unknown"],
    
    # L开头
    "land": ["landed", "landing", "lands", "landlord", "landmark"],
    "last": ["lasted", "lasting", "lasts", "lastly"],
    "laugh": ["laughed", "laughing", "laughs", "laughter"],
    "learn": ["learned", "learning", "learns", "learner", "learnt"],
    "leave": ["left", "leaving", "leaves", "leaver"],
    "lend": ["lent", "lending", "lends", "lender"],
    "let": ["letting", "lets", "let"],
    "lie": ["lay", "lain", "lying", "lied", "liar"],
    "like": ["liked", "liking", "likes", "likely", "unlike"],
    "link": ["linked", "linking", "links", "linkage"],
    "list": ["listed", "listing", "lists", "listless"],
    "listen": ["listened", "listening", "listens", "listener", "listenable"],
    "live": ["lived", "living", "lives", "livable", "lively", "lifestyle"],
    "look": ["looked", "looking", "looks", "looker", "lookout", "looks"],
    "lose": ["lost", "losing", "loses", "loss", "loser", "loseless"],
    "love": ["loved", "loving", "loves", "lovely", "lover", "lovingly"],
    
    # M开头
    "make": ["made", "making", "makes", "maker", "makeshift", "makeup"],
    "manage": ["managed", "managing", "manages", "manager", "management", "manageable"],
    "mean": ["meant", "meaning", "means", "meaningful", "meaningfully", "meaningless", "meantime", "meanwhile"],
    "meet": ["met", "meeting", "meets", "meeting"],
    "might": ["mightier", "mightiest"],
    "move": ["moved", "moving", "moves", "movement", "movable", "mover"],
    
    # N开头
    "need": ["needed", "needing", "needs", "needful", "needless", "needle"],
    "notice": ["noticed", "noticing", "notices", "noticeable", "unnoticeable"],
    
    # O开头
    "obey": ["obeyed", "obeying", "obeys", "obedience", "obedient", " disobedient"],
    "offer": ["offered", "offering", "offers", "offering"],
    "open": ["opened", "opening", "opens", "openly", "openness", "opener", "unopened"],
    "operate": ["operated", "operating", "operates", "operation", "operational", "operator"],
    "order": ["ordered", "ordering", "orders", "orderly", "disorder", "reorder"],
    
    # P开头
    "paint": ["painted", "painting", "paints", "painter", "painting"],
    "pass": ["passed", "passing", "passes", "passage", "passenger", "passing"],
    "pay": ["paid", "paying", "pays", "payment", "payable", "payee", "payer"],
    "perceive": ["perceived", "perceiving", "perceives", "perception", "perceptible"],
    "perform": ["performed", "performing", "performs", "performance", "performer", "performance"],
    "permit": ["permitted", "permitting", "permits", "permission", "permissible"],
    "pick": ["picked", "picking", "picks", "picker"],
    "place": ["placed", "placing", "places", "placement", "replace", "replaceable"],
    "plan": ["planned", "planning", "plans", "planner", "planning"],
    "plant": ["planted", "planting", "plants", "planter", "plantation"],
    "play": ["played", "playing", "plays", "player", "playful", "playground", "playmate"],
    "please": ["pleased", "pleasing", "pleases", "pleasure", "pleasant", "pleasantly"],
    "point": ["pointed", "pointing", "points", "pointed", "pointless", "pointedly"],
    "prepare": ["prepared", "preparing", "prepares", "preparation", "preparable"],
    "present": ["presented", "presenting", "presents", "presentation", "presenter", "presently"],
    "preserve": ["preserved", "preserving", "preserves", "preservation", "preservative"],
    "press": ["pressed", "pressing", "presses", "pressure", "pressing", "pressable"],
    "prevent": ["prevented", "preventing", "prevents", "prevention", "preventive"],
    "produce": ["produced", "producing", "produces", "producer", "production", "productive", "productivity", "products"],
    "promise": ["promised", "promising", "promises", "promisingly", "promiser"],
    "protect": ["protected", "protecting", "protects", "protection", "protective", "protector"],
    "provide": ["provided", "providing", "provides", "provider", "provision", "provisions"],
    "publish": ["published", "publishing", "publishes", "publisher", "publication"],
    
    # R开头
    "raise": ["raised", "raising", "raises", "raiser", "raisin"],
    "reach": ["reached", "reaching", "reaches", "reachable", "reacher"],
    "read": ["read", "reading", "reads", "reader", "readable", "readily", "readiness"],
    "recognize": ["recognized", "recognizing", "recognizes", "recognition", "recognizable"],
    "recommend": ["recommended", "recommending", "recommends", "recommendation", "recommender"],
    "record": ["recorded", "recording", "records", "recorder", "recordable"],
    "reduce": ["reduced", "reducing", "reduces", "reduction", "reducible"],
    "refer": ["referred", "referring", "refers", "reference", "referable"],
    "refuse": ["refused", "refusing", "refuses", "refusal"],
    "regard": ["regarded", "regarding", "regards", "regardless"],
    "register": ["registered", "registering", "registers", "registration", "registrable"],
    "remain": ["remained", "remaining", "remains", "remainder", "remaining"],
    "remember": ["remembered", "remembering", "remembers", "rememberable", "unforgettable"],
    "remind": ["reminded", "reminding", "reminds", "reminder"],
    "remove": ["removed", "removing", "removes", "removal", "remover"],
    "repeat": ["repeated", "repeating", "repeats", "repetition", "repetitive"],
    "reply": ["replied", "replying", "replies", "replyable"],
    "report": ["reported", "reporting", "reports", "reporter", "reporting"],
    "represent": ["represented", "representing", "represents", "representation", "representative", "representational"],
    "require": ["required", "requiring", "requires", "requirement", "requirements", "requirable"],
    "research": ["researched", "researching", "researches", "researcher", "researchable"],
    "respect": ["respected", "respecting", "respects", "respectful", "respectfully", "respectable", "inrespectable"],
    "respond": ["responded", "responding", "responds", "response", "responsive", "responsibly"],
    "rest": ["rested", "resting", "rests", "restful", "restless", "restoration", "restore"],
    "return": ["returned", "returning", "returns", "returnable", "returner"],
    "reveal": ["revealed", "revealing", "reveals", "revelation", "revealer"],
    "rise": ["rose", "risen", "rising", "rises", "riser"],
    "run": ["ran", "run", "running", "runs", "runner", "runnable"],
    
    # S开头
    "say": ["said", "saying", "says", "sayer"],
    "see": ["saw", "seen", "seeing", "sees", "seem", "seemed", "seeming", "seems", "seemingly", "seen"],
    "seek": ["sought", "seeking", "seeks", "seeker"],
    "sell": ["sold", "selling", "sells", "seller", "sellable"],
    "send": ["sent", "sending", "sends", "sender", "sendable"],
    "sense": ["sensed", "sensing", "senses", "sensible", "sensely", "sensitive", "sensitivity"],
    "serve": ["served", "serving", "serves", "server", "service", "servant", "services"],
    "set": ["setting", "settings", "set", "sets"],
    "settle": ["settled", "settling", "settles", "settlement", "settler", "settler"],
    "develop": ["developed", "developing", "develops", "development", "developer"],
    "sew": ["sewed", "sewn", "sewing", "sews", "sewer"],
    "shake": ["shook", "shaken", "shaking", "shakes", "shaker"],
    "shall": ["should", "shoulder"],
    "share": ["shared", "sharing", "shares", " sharer", "shareable"],
    "shed": ["shedding", "sheds", "shedder"],
    "shoot": ["shot", "shooting", "shoots", "shooter", "shooting"],
    "show": ["showed", "shown", "showing", "shows", "showman", "showy"],
    "shut": ["shutting", "shuts", "shutter"],
    "sick": ["sickness", "sickly"],
    "sign": ["signed", "signing", "signs", "signature", "signboard", "signal", "significant", "significantly"],
    "sing": ["sang", "sung", "singing", "sings", "singer", "singing"],
    "sit": ["sat", "sitting", "sits", "sitter"],
    "size": ["sized", "sizing", "sizes", "sizable"],
    "sketch": ["sketched", "sketching", "sketches", "sketcher"],
    "sleep": ["slept", "sleeping", "sleeps", "sleepy", "sleepless", "sleeper"],
    "slide": ["slid", "sliding", "slides", "slider"],
    "slow": ["slowed", "slowing", "slows", "slowly", "slowness", "slower", "slowest"],
    "solve": ["solved", "solving", "solves", "solution", "solutions", "solvable"],
    "sort": ["sorted", "sorting", "sorts", "sorter", "sortable"],
    "sound": ["sounded", "sounding", "sounds", "soundly", "soundness", "unsound"],
    "spend": ["spent", "spending", "spends", "spender"],
    "stand": ["stood", "standing", "stands", "stander", "standpoint"],
    "start": ["started", "starting", "starts", "starter", "starting"],
    "state": ["stated", "stating", "states", "statement", "statesman"],
    "stay": ["stayed", "staying", "stays", "stayer"],
    "steal": ["stole", "stolen", "stealing", "steals", "stealer"],
    "stick": ["stuck", "sticking", "sticks", "sticker", "sticky"],
    "stop": ["stopped", "stopping", "stops", "stopper", "stoppable"],
    "store": ["stored", "storing", "stores", "storekeeper", "storeroom"],
    "strengthen": ["strengthened", "strengthening", "strengthens", "strengthening", "strength", "strong", "strongly", "stronger", "strongest"],
    "study": ["studied", "studying", "studies", "student", "students", "studious"],
    "stuff": ["stuffed", "stuffing", "stuffs", "stuffing"],
    "succeed": ["succeeded", "succeeding", "succeeds", "success", "successful", "successfully", "successor"],
    "suggest": ["suggested", "suggesting", "suggests", "suggestion", "suggestive"],
    "suppose": ["supposed", "supposing", "supposes", "supposition", "supposedly"],
    "surprise": ["surprised", "surprising", "surprises", "surprisingly", "surpriser"],
    "surround": ["surrounded", "surrounding", "surrounds", "surroundings"],
    "switch": ["switched", "switching", "switches", "switcher"],
    "sympathy": ["sympathetic", "sympathetically", "sympathize"],
    
    # T开头
    "take": ["took", "taken", "taking", "takes", "taker", "taken"],
    "talk": ["talked", "talking", "talks", "talker", "talkative"],
    "teach": ["taught", "teaching", "teaches", "teacher", "teachable"],
    "tell": ["told", "telling", "tells", "teller"],
    "think": ["thought", "thinking", "thinks", "thinker", "thinkable", "thoughtful"],
    "throw": ["threw", "thrown", "throwing", "throws", "thrower"],
    "touch": ["touched", "touching", "touches", "touchable", "touchless"],
    "train": ["trained", "training", "trains", "trainer", "trainee", "trainable"],
    "translate": ["translated", "translating", "translates", "translator", "translation", "translatable"],
    "transport": ["transported", "transporting", "transports", "transportation", "transportable"],
    "travel": ["traveled", "traveling", "travels", "traveler", "traveling", "travelling"],
    "treasure": ["treasured", "treasuring", "treasures", "treasurer", "treasurable"],
    "treat": ["treated", "treating", "treats", "treatment", "treatable"],
    "try": ["tried", "trying", "tries", "tryer", "tryable"],
    "turn": ["turned", "turning", "turns", "turner", "turning"],
    
    # U开头
    "understand": ["understood", "understanding", "understands", "understandable", "understandingly"],
    "use": ["used", "using", "uses", "user", "usage", "useful", "usefully", "usefulness", "useless", "unused"],
    
    # V开头
    "value": ["valued", "valuing", "values", "valuable", "valuation", "valuer"],
    "vary": ["varied", "varying", "varies", "variety", "various", "variably"],
    "visit": ["visited", "visiting", "visits", "visitor", "visitable", "visiting"],
    "vote": ["voted", "voting", "votes", "voter", "voting"],
    
    # W开头
    "wake": ["woke", "woken", "waking", "wakes", "wakeful", "awake"],
    "walk": ["walked", "walking", "walks", "walker", "walkway"],
    "want": ["wanted", "wanting", "wants", "wanting"],
    "warn": ["warned", "warning", "warns", "warning", "warner"],
    "wash": ["washed", "washing", "washes", "washer", "washable"],
    "watch": ["watched", "watching", "watches", "watcher", "watchful"],
    "wear": ["wore", "worn", "wearing", "wears", "wearer", "wearable"],
    "wed": ["wedding", "weddings"],
    "weigh": ["weighed", "weighing", "weighs", "weight", "weightless", "weighable"],
    "welcome": ["welcomed", "welcoming", "welcomes", "welcomeable"],
    "will": ["would", "willing", "willingly", "willingness"],
    "win": ["won", "winning", "wins", "winner", "winning"],
    "wind": ["wound", "winding", "winds", "windy"],
    "wish": ["wished", "wishing", "wishes", "wishful", "wishbone"],
    "wonder": ["wondered", "wondering", "wonders", "wonderful", "wonderfully", "wonderment"],
    "work": ["worked", "working", "works", "worker", "working", "workable", "workaday", "workbook", "workforce", "workhouse", "workload", "workman", "workmate", "workplace", "worksheet", "workshop", "workspace", "workstation", "worktable", "workflow", "workout", "workroom", "worktop", "workwear", "working", "working", "workmanship", "workaday", "workaholic", "workaday", "workbench", "workbook", "workday", "worker", "workforce", "workhouse", "workload", "workman", "workmate", "workplace", "workroom", "works", "worksheet", "workshop", "workspace", "workstation", "worktable", "worktop", "workwear", "working", "workmanship", "workflow", "workout", "workroom", "worktop", "workwear", "working", "workman", "workmate", "workplace", "workroom", "works", "worksheet", "workshop", "workspace", "workstation", "worktable", "worktop", "workwear"],
    "wrap": ["wrapped", "wrapping", "wraps", "wrapper", "wrapable"],
    
    # Y开头
    "yell": ["yelled", "yelling", "yells", "yeller"],
    "yield": ["yielded", "yielding", "yields", "yielding"],
    
    # Z开头
    "zip": ["zipped", "zipping", "zips", "zipper", "zipless"],
}

def read_vocab_from_md(md_file: Path) -> List[Tuple[str, str, str]]:
    """从Markdown文件读取词汇表"""
    words = []
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    pattern = r'- \*\*([a-zA-Z]+)\*\* \[([^\]]+)\]  (.+)'
    matches = re.findall(pattern, content)
    
    for match in matches:
        word, phonetic, meaning = match
        words.append((word, phonetic, meaning))
    
    return words

def generate_association_card(word: str, phonetic: str, meaning: str, family_list: List[str]) -> str:
    """生成单个词的联想记忆卡片"""
    card = f"## {word}\n\n"
    card += f"- **音标**: {phonetic}\n"
    card += f"- **释义**: {meaning}\n\n"
    
    if family_list:
        card += f"- **词族联想**:\n"
        for related_word in family_list[:10]:  # 最多显示10个
            card += f"  - {related_word}\n"
    
    card += "\n"
    return card

def generate_all_cards(vocab_data: List[Tuple[str, str, str]], output_file: Path):
    """生成所有词的联想记忆卡片"""
    all_cards = []
    
    # 标题
    all_cards.append("# 深圳中考英语联想记忆卡片\n\n")
    all_cards.append("> 基于《义务教育英语课程标准》（2022年版）\n\n")
    all_cards.append("> 每个词汇配有词族联想记忆，帮助快速记忆和拓展词汇量\n\n")
    all_cards.append("---\n\n")
    
    # 按词族分组
    generated_count = 0
    for word, phonetic, meaning in vocab_data:
        word_lower = word.lower()
        
        if word_lower in WORD_FAMILY_DICT:
            family = WORD_FAMILY_DICT[word_lower]
            card = generate_association_card(word, phonetic, meaning, family)
            all_cards.append(card)
            generated_count += 1
    
    # 写入文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(all_cards)
    
    return generated_count

def main():
    print("=" * 60)
    print("联想记忆卡片生成工具")
    print("=" * 60)
    
    script_dir = Path(__file__).parent
    md_file = script_dir / "词汇表.md"
    output_file = script_dir / "联想记忆卡片.md"
    
    # 1. 读取词汇表
    print("\n1. 读取词汇表...")
    if not md_file.exists():
        print(f"   ✗ 找不到词汇表文件: {md_file}")
        return
    
    vocab_data = read_vocab_from_md(md_file)
    print(f"   ✓ 读取到 {len(vocab_data)} 个词汇")
    
    # 2. 生成联想记忆卡片
    print("\n2. 生成联想记忆卡片...")
    generated_count = generate_all_cards(vocab_data, output_file)
    print(f"   ✓ 已生成 {generated_count} 个联想记忆卡片")
    print(f"   ✓ 输出文件: {output_file}")
    
    # 3. 统计信息
    print("\n3. 统计信息:")
    print(f"   - 词汇表总词数: {len(vocab_data)}")
    print(f"   - 生成联想卡片数: {generated_count}")
    print(f"   - 覆盖率: {generated_count/len(vocab_data)*100:.1f}%")
    
    # 4. 显示示例
    print("\n4. 示例卡片（前3个）:")
    sample_words = ['able', 'accept', 'ache']
    for word in sample_words:
        for w, p, m in vocab_data:
            if w.lower() == word:
                family = WORD_FAMILY_DICT.get(word.lower(), [])
                print(f"\n   ## {word}")
                print(f"   音标: {p}")
                print(f"   释义: {m}")
                print(f"   词族: {', '.join(family[:5])}...")
                break
    
    print("\n" + "=" * 60)
    print("完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()
