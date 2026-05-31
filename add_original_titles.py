#!/usr/bin/env python3
"""批量为翻译书籍添加 originalTitle 字段"""
import os, re

BOOKS_DIR = "/root/my-blog/src/content/books"

# 知名翻译书籍的 originalTitle 映射（slug → originalTitle）
KNOWN = {
    "1984": "Nineteen Eighty-Four",
    "不能承受的生命之轻": "The Unbearable Lightness of Being",
    "与罗摩相会": "Rendezvous with Rama",
    "东方快车谋杀案": "Murder on the Orient Express",
    "丝绸之路-一部全新的世界史": "The Silk Roads: A New History of the World",
    "乌合之众": "The Crowd: A Study of the Popular Mind",
    "了不起的盖茨比": "The Great Gatsby",
    "人类简史": "Sapiens: A Brief History of Humankind",
    "仿生人会梦见电子羊吗": "Do Androids Dream of Electric Sheep?",
    "你一生的故事": "Stories of Your Life and Others",
    "信息简史": "The Information: A History, a Theory, a Flood",
    "信息论、推理与学习算法": "Information Theory, Inference, and Learning Algorithms",
    "傲慢与偏见": "Pride and Prejudice",
    "元素的盛宴": "The Disappearing Spoon",
    "全球通史": "A Global History",
    "关键对话": "Crucial Conversations: Tools for Talking When Stakes Are High",
    "具体数学-计算机科学基础": "Concrete Mathematics: A Foundation for Computer Science",
    "最好的告别": "Being Mortal: Medicine and What Matters in the End",
    "动手学深度学习": "Dive into Deep Learning",
    "动物农场": "Animal Farm",
    "助推": "Nudge: Improving Decisions About Health, Wealth, and Happiness",
    "包法利夫人": "Madame Bovary",
    "博尔赫斯短篇小说集": "Ficciones",
    "卡拉马佐夫兄弟": "The Brothers Karamazov",
    "历史的教训": "The Lessons of History",
    "双城记": "A Tale of Two Cities",
    "变形记": "Die Verwandlung",
    "史蒂夫-乔布斯传": "Steve Jobs",
    "合作的进化": "The Evolution of Cooperation",
    "周期表": "Il Sistema Periodico",
    "呼啸山庄": "Wuthering Heights",
    "哈佛中国史": "History of Imperial China",
    "哥德尔、艾舍尔、巴赫-集异璧之大成": "Gödel, Escher, Bach: An Eternal Golden Braid",
    "哲学问题": "The Problems of Philosophy",
    "国富论": "An Inquiry into the Nature and Causes of the Wealth of Nations",
    "基因传": "The Gene: An Intimate History",
    "基督山伯爵": "Le Comte de Monte-Cristo",
    "堂吉诃德": "Don Quixote",
    "复分析-可视化方法": "Visual Complex Analysis",
    "大国政治的悲剧": "The Tragedy of Great Power Politics",
    "大设计": "The Grand Design",
    "天真的人类学家": "The Innocent Anthropologist: Notes from a Mud Hut",
    "奥德赛": "The Odyssey",
    "如何阅读一本书": "How to Read a Book",
    "娱乐至死": "Amusing Ourselves to Death: Public Discourse in the Age of Show Business",
    "嫌疑人X的献身": "容疑者Xの献身",
    "存在与虚无": "L'Être et le Néant",
    "学会提问": "Asking the Right Questions: A Guide to Critical Thinking",
    "宇宙": "Cosmos",
    "安娜-卡列尼娜": "Anna Karenina",
    "安德的游戏": "Ender's Game",
    "寂静的春天": "Silent Spring",
    "密码故事": "The Code Book: The Science of Secrecy from Ancient Egypt to Quantum Cryptography",
    "小王子": "Le Petit Prince",
    "尼各马可伦理学": "Nicomachean Ethics",
    "局外人": "L'Étranger",
    "巴黎圣母院": "Notre-Dame de Paris",
    "希腊棺材之谜": "The Greek Coffin Mystery",
    "影响力": "Influence: The Psychology of Persuasion",
    "掌控谈话": "Never Split the Difference",
    "理论最小值-经典力学": "The Theoretical Minimum: Classical Mechanics",
    "程序员修炼之道-通向务实的最高境界": "The Pragmatic Programmer: Your Journey to Mastery",
    "经济学的思维方式": "The Economic Way of Thinking",
    "结构是什么": "Structures: Or Why Things Don't Fall Down",
    "自私的基因": "The Selfish Gene",
    "规模": "Scale: The Universal Laws of Growth, Innovation, Sustainability",
    "银河帝国-基地七部曲": "Foundation (series)",
    "非暴力沟通": "Nonviolent Communication: A Language of Life",
    "呼吸": "Exhalation: Stories",
    "九人-美国最高法院风云": "The Nine: Inside the Secret World of the Supreme Court",
    "别闹了，费曼先生": "Surely You're Joking, Mr. Feynman!",
    "刻意练习": "Peak: Secrets from the New Science of Expertise",
    "万物简史": "A Short History of Nearly Everything",
    "从一到无穷大": "One Two Three... Infinity",
    "什么是数学": "What Is Mathematics? An Elementary Approach to Ideas and Methods",
    "初等数论": "Elementary Number Theory",
    "化学简史": "A Short History of Chemistry",
    "大脑的故事": "The Brain: The Story of You",
    "嵌入式系统导论": "Introduction to Embedded Systems",
    "图论导引": "Introduction to Graph Theory",
    "周期表": "Il Sistema Periodico",
    "为什么学生不喜欢上学": "Why Don't Students Like School?",
    "大设计": "The Grand Design",
    "费曼物理学讲义": "The Feynman Lectures on Physics",
    "数据密集型应用系统设计": "Designing Data-Intensive Applications",
    "深入理解计算机系统": "Computer Systems: A Programmer's Perspective",
    "线性代数应该这样学": "Linear Algebra Done Right",
    "概率论导论": "Introduction to Probability",
    "统计学习导论": "An Introduction to Statistical Learning",
    "计算机视觉-算法与应用": "Computer Vision: Algorithms and Applications",
    "机器学习实战": "Machine Learning in Action",
    "白帽子讲Web安全": "Web Security for White Hat Hackers",
    "编码-隐匿在计算机软硬件背后的语言": "Code: The Hidden Language of Computer Hardware and Software",
    "社会心理学": "Social Psychology",
    "微积分": "Calculus",
    "我们世界的历史": "The History of the World",
    "泰晤士世界历史地图集": "The Times Atlas of World History",
    "计算机程序的构造和解释": "Structure and Interpretation of Computer Programs",
    "计算机图形学": "Computer Graphics",
    "自私的基因": "The Selfish Gene",
    "规模": "Scale",
    "写给大家的西方美术史": "A History of Western Art",
    "最好的告别": "Being Mortal",
    "基因传": "The Gene: An Intimate History",
    "1453-君士坦丁堡的陷落": "1453: The Holy War for Constantinople and the Clash of Islam and the West",
    "三体": None,  # 中文原创
    "三国演义": None,
    "红楼梦": None,
    "水浒传": None,
    "西游记": None,
}

# 中文书作者特征（不需要 originalTitle）
def is_chinese_original(author, title_slug):
    """判断是否中文原创书籍"""
    if title_slug in KNOWN:
        return KNOWN[title_slug] is None
    # 作者名包含拉丁字母 → 很可能是翻译
    if re.search(r'[a-zA-Z]{3,}', author):
        return False
    return True

def parse_and_update(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    m = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not m:
        return None
    
    raw = m.group(1)
    body = content[m.end():]
    
    # 解析字段
    data = {}
    for line in raw.split('\n'):
        line = line.strip()
        if ':' in line:
            key, _, value = line.partition(':')
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            data[key] = value
    
    title = data.get('title', '')
    author = data.get('author', '')
    slug = os.path.basename(filepath)[:-3]
    
    # 已有 originalTitle → 跳过
    if 'originalTitle' in data:
        return 'skip'
    
    # 查找已知映射
    if slug in KNOWN:
        ot = KNOWN[slug]
        if ot is None:
            return 'chinese_original'
    else:
        # 未在已知列表，根据作者名判断
        if is_chinese_original(author, slug):
            return 'chinese_original'
        else:
            # 翻译书但未知原名，跳过
            return 'unknown'
    
    # 插入 originalTitle 到 frontmatter
    ot = KNOWN[slug]
    # 在 title 行之后插入
    new_raw = re.sub(
        r'(^title:\s*".*?"\n)',
        f'\\1originalTitle: "{ot}"\n',
        raw,
        count=1
    )
    
    new_content = f'---\n{new_raw}\n---{body}'
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return 'updated'

def main():
    files = sorted([f for f in os.listdir(BOOKS_DIR) if f.endswith('.md')])
    
    updated = 0
    skipped = 0
    chinese = 0
    unknown = 0
    
    for fname in files:
        filepath = os.path.join(BOOKS_DIR, fname)
        result = parse_and_update(filepath)
        
        slug = fname[:-3]
        
        if result == 'updated':
            updated += 1
            ot = KNOWN.get(slug, '?')
            print(f"✅ {slug} → {ot}")
        elif result == 'skip':
            skipped += 1
        elif result == 'chinese_original':
            chinese += 1
        elif result == 'unknown':
            unknown += 1
            print(f"❓ {slug} (翻译书但未知原名)")
    
    print(f"\n{'='*50}")
    print(f"📊 总计: {len(files)} 本")
    print(f"✅ 已添加 originalTitle: {updated}")
    print(f"⏭ 已有 originalTitle: {skipped}")
    print(f"🇨🇳 中文原创: {chinese}")
    print(f"❓ 翻译书未知原名: {unknown}")

if __name__ == '__main__':
    main()
