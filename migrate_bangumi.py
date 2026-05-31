#!/usr/bin/env python3
"""从 bangumi_ratings_yzher.json 迁移到博客内容"""
import json, os, re

JSON_FILE = "/root/my-blog/bangumi_ratings_yzher.json"
MOVIES_DIR = "/root/my-blog/src/content/movies"
GAMES_DIR = "/root/my-blog/src/content/games"

os.makedirs(MOVIES_DIR, exist_ok=True)
os.makedirs(GAMES_DIR, exist_ok=True)

with open(JSON_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

def safe_slug(name, bid):
    """生成安全的文件名"""
    s = name.replace('/', '-').replace(':', '：').replace('?', '').replace('~', '')
    s = re.sub(r'[\\\*\<\>\|]', '', s)
    return s

created_anime = 0
created_game = 0
skipped = 0

for item in data:
    stype = item['subject_type']
    bid = item['subject_id']
    name = item.get('name', '')
    name_orig = item.get('name_orig', '')
    rate = item['rate']
    coll = item.get('collection_type', '')
    comment = item.get('comment', '')
    date_str = item.get('date', '2026-01-01')
    
    # 提取年份
    year = int(date_str[:4]) if date_str else 2026
    
    # 决定目标目录和 frontmatter
    if stype == '动画':
        target_dir = MOVIES_DIR
        slug = safe_slug(name, bid)
        filepath = os.path.join(target_dir, f"{slug}.md")
        if os.path.exists(filepath):
            skipped += 1
            continue
        
        fm = f'''---
title: "{name}"
originalTitle: "{name_orig}"
poster: ""
rating: {rate}
bgmid: {bid}
watchDate: {date_str}
year: {year}
type: "动画"
tags: []
summary: ""
---
'''
        body = f'> {coll}\n'
        if comment:
            body += f'\n{comment}\n'
        created_anime += 1
        
    elif stype == '游戏':
        target_dir = GAMES_DIR
        slug = safe_slug(name, bid)
        filepath = os.path.join(target_dir, f"{slug}.md")
        if os.path.exists(filepath):
            skipped += 1
            continue
        
        # 猜测平台（不精确，后续手动修正）
        platform = 'PC'
        
        fm = f'''---
title: "{name}"
originalTitle: "{name_orig}"
developer: ""
poster: ""
rating: {rate}
bgmid: {bid}
playDate: {date_str}
year: {year}
platform: "{platform}"
tags: []
summary: ""
---
'''
        body = f'> {coll}\n'
        if comment:
            body += f'\n{comment}\n'
        created_game += 1
    else:
        continue
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(fm + body)

print(f"✅ 动画: {created_anime} 部")
print(f"✅ 游戏: {created_game} 款")
print(f"⏭ 跳过(已存在): {skipped}")
print(f"\n📊 共 {created_anime + created_game} 条待获取封面")
