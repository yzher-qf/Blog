#!/usr/bin/env python3
"""修正 originalTitle：原语言名称 + 移除中文书的 originalTitle"""
import os, re

BOOKS_DIR = "/root/my-blog/src/content/books"

FIXES = {
    # === 俄语原著 → 用俄文 ===
    "卡拉马佐夫兄弟": "Братья Карамазовы",
    "安娜-卡列尼娜": "Анна Каренина",
    # === 捷克语 ===
    "不能承受的生命之轻": "Nesnesitelná lehkost bytí",
    # === 西班牙语 ===
    "堂吉诃德": "Don Quijote de la Mancha",
    # === 机器学习实战：原名是 Géron 的书，不是 "Machine Learning in Action" ===
    "机器学习实战": "Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow",
}

# 中文作者 → 应移除 originalTitle
REMOVE_OT = {
    "写给大家的西方美术史",  # 蒋勋
    "初等数论",              # 闵嗣鹤
    "白帽子讲Web安全",       # 吴翰清
}

def process_file(filepath, slug):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    m = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not m:
        return None
    raw = m.group(1)
    body = content[m.end():]
    
    if slug in FIXES:
        new_ot = FIXES[slug]
        # 替换 originalTitle 行
        new_raw = re.sub(
            r'^originalTitle:\s*".*?"\s*$',
            f'originalTitle: "{new_ot}"',
            raw,
            flags=re.MULTILINE
        )
        if new_raw != raw:
            new_content = f'---\n{new_raw}\n---{body}'
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return f'fixed → {new_ot}'
        return 'no_change'
    
    if slug in REMOVE_OT:
        # 移除 originalTitle 行
        new_raw = re.sub(
            r'^originalTitle:\s*".*?"\s*\n',
            '',
            raw,
            flags=re.MULTILINE
        )
        if new_raw != raw:
            new_content = f'---\n{new_raw}\n---{body}'
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return 'removed (Chinese original)'
        return 'no_change'
    
    return None

def main():
    files = sorted([f for f in os.listdir(BOOKS_DIR) if f.endswith('.md')])
    
    for fname in files:
        filepath = os.path.join(BOOKS_DIR, fname)
        slug = fname[:-3]
        result = process_file(filepath, slug)
        if result:
            print(f'{result:40s} ← {slug}')

if __name__ == '__main__':
    main()
