#!/usr/bin/env python3
"""第 3 轮：逐一审查所有书籍，为漏网的翻译书添加 originalTitle"""

# 格式: slug → originalTitle
# 中文原创不在此列表
ADD = {
    # === 文学 / 小说 ===
    "三口棺材": "The Three Coffins",
    "契诃夫短篇小说选": "Рассказы",
    "悲惨世界": "Les Misérables",
    "战争与和平": "Война и мир",
    "挪威的森林": "ノルウェイの森",
    "月亮和六便士": "The Moon and Sixpence",
    "杀死一只知更鸟": "To Kill a Mockingbird",
    "洛丽塔": "Lolita",
    "沙丘": "Dune",
    "白鲸": "Moby-Dick",
    "百年孤独": "Cien años de soledad",
    "简-爱": "Jane Eyre",
    "红与黑": "Le Rouge et le Noir",
    "罪与罚": "Преступление и наказание",
    "美丽新世界": "Brave New World",
    "老人与海": "The Old Man and the Sea",
    "霍乱时期的爱情": "El amor en los tiempos del cólera",
    "魔戒": "The Lord of the Rings",
    "麦田里的守望者": "The Catcher in the Rye",
    "雾都孤儿": "Oliver Twist",
    "雪国": "雪国",
    "白夜行": "白夜行",
    "恶意": "悪意",
    "源氏物语": "源氏物語",
    "漫长的告别": "The Long Goodbye",
    "无人生还": "And Then There Were None",
    "福尔摩斯探案全集": "The Complete Sherlock Holmes",
    "海伯利安": "Hyperion",
    "神经漫游者": "Neuromancer",
    "莱博维茨的赞歌": "A Canticle for Leibowitz",
    "看不见的城市": "Le città invisibili",
    "瓦尔登湖": "Walden",

    # === 哲学 / 思想 ===
    "沉思录": "Τὰ εἰς ἑαυτόν",
    "理想国": "Πολιτεία",
    "查拉图斯特拉如是说": "Also sprach Zarathustra",
    "西西弗神话": "Le Mythe de Sisyphe",
    "纯粹理性批判": "Kritik der reinen Vernunft",
    "第一哲学沉思集": "Meditationes de Prima Philosophia",
    "蒙田随笔": "Essais",
    "浮士德": "Faust",
    "神曲": "La Divina Commedia",
    "论犯罪与刑罚": "Dei delitti e delle pene",
    "西方哲学史": "A History of Western Philosophy",
    "被讨厌的勇气": "嫌われる勇気",

    # === 科普 / 科学 ===
    "时间简史": "A Brief History of Time",
    "暗淡蓝点": "Pale Blue Dot",
    "物理学的进化": "The Evolution of Physics",
    "物种起源": "On the Origin of Species",
    "生命是什么": "What Is Life?",
    "枪炮、病菌与钢铁": "Guns, Germs, and Steel",
    "心智探奇": "How the Mind Works",
    "语言本能": "The Language Instinct",
    "我们赖以生存的隐喻": "Metaphors We Live By",
    "科学革命的结构": "The Structure of Scientific Revolutions",
    "相同与不同": "The Same and Not the Same",
    "迷人的材料": "Stuff Matters",
    "致命元素-毒药的历史": "The Elements of Murder: A History of Poison",
    "气候改变世界": "The Great Warming: Climate Change and the Rise and Fall of Civilizations",
    "能源与文明": "Energy and Civilization: A History",
    "海洋传": "The Sea Around Us",

    # === 心理学 / 社会学 ===
    "思考，快与慢": "Thinking, Fast and Slow",
    "心理学与生活": "Psychology and Life",
    "社会性动物": "The Social Animal",
    "自卑与超越": "What Life Could Mean to You",
    "活出生命的意义": "…trotzdem Ja zum Leben sagen",
    "狂热分子": "The True Believer",
    "道德动物": "The Moral Animal",
    "设计心理学": "The Design of Everyday Things",
    "高效能人士的七个习惯": "The 7 Habits of Highly Effective People",
    "社会学": "Sociology",
    "组织行为学": "Organizational Behavior",
    "贫穷的本质": "Poor Economics",

    # === 经济 / 商业 ===
    "经济学原理": "Principles of Economics",
    "漫步华尔街": "A Random Walk Down Wall Street",
    "策略思维": "Thinking Strategically",
    "金字塔原理": "The Pyramid Principle",

    # === 法律 ===
    "洞穴奇案": "The Case of the Speluncean Explorers: Nine New Opinions",
    "法律的故事": "The Story of Law",

    # === 历史 ===
    "海洋帝国-地中海大决战": "Empires of the Sea: The Siege of Malta, the Battle of Lepanto, and the Contest for the Center of the World",

    # === 艺术 ===
    "艺术的故事": "The Story of Art",
    "聆听音乐": "Listening to Music",

    # === 语言 ===
    "汉语的本质和历史": "The Chinese Language: An Essay on Its Nature and History",
    "语言兴衰论": "The Rise and Fall of Languages",
    "风格的要素": "The Elements of Style",

    # === 教材 / 学术 ===
    "逻辑学导论": "Introduction to Logic",
    "运筹学导论": "Introduction to Operations Research",
    "政治学": "Politics",
    "当代天体物理学导论": "An Introduction to Modern Astrophysics",
    "苏菲的世界": "Sofies verden",
}

import os, re

BOOKS_DIR = "/root/my-blog/src/content/books"

def process(slug):
    filepath = os.path.join(BOOKS_DIR, f"{slug}.md")
    if not os.path.exists(filepath):
        return 'NOT FOUND'
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    m = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not m:
        return 'no frontmatter'
    
    raw = m.group(1)
    body = content[m.end():]
    
    if 'originalTitle:' in raw:
        return 'already has OT'
    
    ot = ADD[slug]
    # 在 title 行之后插入
    new_raw = re.sub(
        r'(^title:\s*".*?"\n)',
        f'\\1originalTitle: "{ot}"\n',
        raw,
        count=1
    )
    
    if new_raw == raw:
        # title 行可能用单引号或不同格式
        new_raw = re.sub(
            r'(^title:\s*.*?\n)',
            f'\\1originalTitle: "{ot}"\n',
            raw,
            count=1
        )
    
    new_content = f'---\n{new_raw}\n---{body}'
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    return f'✅ {ot}'

def main():
    added = 0
    skipped = 0
    
    for slug in sorted(ADD.keys()):
        result = process(slug)
        if result.startswith('✅'):
            added += 1
            print(f'{result:60s} ← {slug}')
        else:
            skipped += 1
            print(f'  {result:58s} ← {slug}')
    
    print(f'\n{"="*50}')
    print(f'✅ 新增: {added} 本')
    print(f'⏭ 跳过: {skipped} 本')

if __name__ == '__main__':
    main()
