#!/usr/bin/env python3
"""通过 Open Library API 为书籍匹配封面"""
import os, re, time, json, urllib.request, urllib.parse

BOOKS_DIR = "/root/my-blog/src/content/books"

def parse_frontmatter(filepath):
    """解析 markdown 文件的 frontmatter"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return None, content
    
    frontmatter = match.group(1)
    body = content[match.end():]
    
    data = {}
    for line in frontmatter.split('\n'):
        line = line.strip()
        if ':' in line:
            key, _, value = line.partition(':')
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            data[key] = value
    
    return data, content

def search_openlibrary(title, author):
    """搜索 Open Library 获取封面 ID"""
    try:
        # URL 编码
        query = urllib.parse.quote(f'{title} {author}')
        url = f'https://openlibrary.org/search.json?q={query}&limit=3'
        
        req = urllib.request.Request(url, headers={'User-Agent': 'MyBlog/1.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        
        docs = data.get('docs', [])
        for doc in docs:
            cover_id = doc.get('cover_i')
            if cover_id:
                return f'https://covers.openlibrary.org/b/id/{cover_id}-L.jpg'
        
        return None
    except Exception as e:
        return None

def main():
    files = sorted([f for f in os.listdir(BOOKS_DIR) if f.endswith('.md')])
    
    total = 0
    found = 0
    skipped = 0
    
    for filename in files:
        filepath = os.path.join(BOOKS_DIR, filename)
        data, content = parse_frontmatter(filepath)
        
        if not data:
            continue
        
        # 跳过已有封面的（非空字符串）
        current_cover = data.get('cover', '')
        if current_cover and current_cover.strip():
            skipped += 1
            continue
        
        title = data.get('title', '')
        author = data.get('author', '')
        
        if not title:
            continue
        
        total += 1
        print(f"🔍 [{total}] {title} ({author}) ...", end=' ')
        
        cover_url = search_openlibrary(title, author)
        
        if cover_url:
            # 更新文件中的 cover 字段
            new_content = re.sub(
                r'cover:\s*""',
                f'cover: "{cover_url}"',
                content,
                count=1
            )
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            found += 1
            print(f"✅ 已匹配")
        else:
            print(f"❌ 未找到")
        
        # 控制频率，避免被封
        time.sleep(0.5)
    
    print(f"\n{'='*50}")
    print(f"📊 共计扫描 {len(files)} 个文件")
    print(f"🔍 需匹配: {total} 本")
    print(f"✅ 匹配成功: {found} 本")
    print(f"⏭ 已有封面跳过: {skipped} 本")
    print(f"❌ 未找到: {total - found} 本")

if __name__ == '__main__':
    main()
