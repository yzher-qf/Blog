#!/usr/bin/env python3
"""通过 Bangumi (bgm.tv) API 为游戏和影视匹配封面"""
import os, re, json, urllib.request, urllib.parse, time

GAMES_DIR = "/root/my-blog/src/content/games"
MOVIES_DIR = "/root/my-blog/src/content/movies"
HEADERS = {'User-Agent': 'YzherBlog/1.0 (https://yzher.xyz)'}

def parse_frontmatter(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    m = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not m:
        return None, content
    raw = m.group(1)
    body = content[m.end():]
    data = {}
    for line in raw.split('\n'):
        if ':' in line:
            k, _, v = line.partition(':')
            data[k.strip()] = v.strip().strip('"').strip("'")
    return data, raw, body

def search_bangumi(keyword, subject_type=2):
    """
    subject_type: 1=书籍, 2=动画, 3=音乐, 4=游戏, 6=三次元
    """
    try:
        query = urllib.parse.quote(keyword)
        url = f'https://api.bgm.tv/search/subject/{query}?type={subject_type}&responseGroup=small&max_results=3'
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        
        # Bangumi API v0 返回 list 包裹在 "list" 字段
        items = data.get('list', data) if isinstance(data, dict) else data
        if isinstance(items, list) and len(items) > 0:
            item = items[0]
            img = item.get('images', {}).get('large', '') or item.get('images', {}).get('common', '')
            return img
        return None
    except Exception as e:
        return None

def get_subject_by_id(bgmid):
    """通过 Bangumi 条目 ID 精确获取封面"""
    try:
        url = f'https://api.bgm.tv/v0/subjects/{bgmid}'
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        img = data.get('images', {}).get('large', '') or data.get('images', {}).get('common', '')
        return img
    except Exception as e:
        return None

def update_cover(filepath, raw_fm, body, cover_url, field='poster'):
    """更新 frontmatter 中的封面字段"""
    new_raw = re.sub(
        rf'^{field}:\s*".*?"',
        f'{field}: "{cover_url}"',
        raw_fm,
        flags=re.MULTILINE
    )
    new_content = f'---\n{new_raw}\n---{body}'
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

def process_dir(directory, content_type, bangumi_type):
    """处理一个内容目录"""
    if not os.path.isdir(directory):
        return
    
    files = sorted([f for f in os.listdir(directory) if f.endswith('.md')])
    found = 0
    skipped = 0
    
    for fname in files:
        filepath = os.path.join(directory, fname)
        data, raw_fm, body = parse_frontmatter(filepath)
        if not data:
            continue
        
        field = 'poster'
        current = data.get(field, '')
        if current and current.strip() and current != '""':
            skipped += 1
            continue
        
        title = data.get('title', '')
        ot = data.get('originalTitle', '')
        bgmid = data.get('bgmid', '')
        
        # 优先用 bgmid 精确获取
        cover_url = None
        if bgmid:
            cover_url = get_subject_by_id(bgmid)
        else:
            search_q = ot if ot else title
            if search_q:
                cover_url = search_bangumi(search_q, bangumi_type)
        
        print(f"🔍 [{content_type}] {title} ...", end=' ')
        
        if cover_url:
            update_cover(filepath, raw_fm, body, cover_url, field)
            found += 1
            print(f"✅ {cover_url[:60]}...")
        else:
            print("❌ 未找到")
        
        time.sleep(0.6)
    
    print(f"\n📊 {content_type}: 找到 {found} 个封面，跳过 {skipped} 个（已有封面）")

def main():
    print("=" * 60)
    print("🎨 Bangumi 封面匹配工具")
    print("=" * 60)
    
    process_dir(GAMES_DIR, "游戏", 4)    # type=4 游戏
    process_dir(MOVIES_DIR, "影视", 2)   # type=2 动画 (Bangumi 主要是二次元)

if __name__ == '__main__':
    main()
