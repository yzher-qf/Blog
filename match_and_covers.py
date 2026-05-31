#!/usr/bin/env python3
"""
电子书文件名匹配 + 封面提取工具

功能：
1. 扫描 public/uploads/ 中的 PDF/EPUB 文件
2. 与 src/content/books/*.md 模糊匹配
3. 从 PDF（pdftoppm）和 EPUB（unzip）提取封面到 public/covers/
4. 更新书籍 markdown 的 cover 字段

用法: python3 match_and_covers.py
"""

import os, re, json, subprocess, tempfile, shutil

UPLOADS_DIR = "/root/my-blog/public/uploads"
BOOKS_DIR = "/root/my-blog/src/content/books"
COVERS_DIR = "/root/my-blog/public/covers"

def normalize(s: str) -> str:
    """标准化字符串用于匹配：去标点、空格、转小写"""
    # 中文标点 → 英文
    trans = str.maketrans({
        '：': ' ', '：': ' ', '，': ' ', '、': ' ', '。': ' ',
        '？': ' ', '！': ' ', '；': ' ', '：': ' ',
        '（': ' ', '）': ' ', '《': ' ', '》': ' ',
        '—': ' ', '·': ' ', '「': ' ', '」': ' ',
        '-': ' ', ':': ' ', ',': ' ', '.': ' ',
        '(': ' ', ')': ' ', '/': ' ', '\\': ' ',
        "'": '', '"': '', '：': ' ',
    })
    s = s.translate(trans)
    # 移除多余空格
    s = re.sub(r'\s+', ' ', s).strip().lower()
    return s

def tokenize(s: str) -> set:
    """将字符串拆分为 token 集合"""
    return set(normalize(s).split())

def parse_frontmatter(filepath):
    """解析 markdown 文件的 frontmatter，返回 (data_dict, raw_frontmatter, body)"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    m = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not m:
        return None, '', content
    
    raw = m.group(1)
    body = content[m.end():]
    
    data = {}
    for line in raw.split('\n'):
        line = line.strip()
        if ':' in line:
            key, _, value = line.partition(':')
            key = key.strip()
            value = value.strip()
            # 去掉引号
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1]
            data[key] = value
    
    return data, raw, body

def load_books():
    """加载所有书籍信息，返回 [{slug, title, author, filepath, data, raw_fm, body}, ...]"""
    books = []
    for fname in sorted(os.listdir(BOOKS_DIR)):
        if not fname.endswith('.md'):
            continue
        filepath = os.path.join(BOOKS_DIR, fname)
        slug = fname[:-3]  # 去掉 .md
        data, raw_fm, body = parse_frontmatter(filepath)
        if not data:
            continue
        books.append({
            'slug': slug,
            'title': data.get('title', slug),
            'author': data.get('author', ''),
            'filepath': filepath,
            'data': data,
            'raw_fm': raw_fm,
            'body': body,
        })
    return books

def load_uploads():
    """加载 uploads 目录文件，返回 [{filename, stem, ext, path}, ...]"""
    files = []
    if not os.path.isdir(UPLOADS_DIR):
        return files
    for fname in os.listdir(UPLOADS_DIR):
        ext_match = re.search(r'\.(pdf|epub|mobi|azw3|txt)$', fname, re.I)
        if not ext_match:
            continue
        ext = ext_match.group(1).lower()
        stem = fname[:ext_match.start()]
        files.append({
            'filename': fname,
            'stem': stem,
            'ext': ext,
            'path': os.path.join(UPLOADS_DIR, fname),
        })
    return files

def match_score(book, upload):
    """计算书籍与上传文件的匹配得分"""
    score = 0
    
    # 1. slug 精确匹配
    if book['slug'] == upload['stem']:
        score += 100
    
    # 2. 标准化后完全匹配
    if normalize(book['slug']) == normalize(upload['stem']):
        score += 90
    
    # 3. title 精确匹配 stem
    if book['title'] == upload['stem']:
        score += 95
    
    # 4. 标准化 title 匹配
    if normalize(book['title']) == normalize(upload['stem']):
        score += 85
    
    # 5. Token 重叠度
    book_tokens = tokenize(book['slug'])
    title_tokens = tokenize(book['title'])
    all_book_tokens = book_tokens | title_tokens
    upload_tokens = tokenize(upload['stem'])
    
    if all_book_tokens and upload_tokens:
        overlap = all_book_tokens & upload_tokens
        jaccard = len(overlap) / len(all_book_tokens | upload_tokens)
        score += jaccard * 50
    
    # 6. 书名是上传文件名的子串
    if len(book['title']) >= 3 and book['title'] in upload['stem']:
        score += 40
    
    # 7. slug 是上传文件名的子串
    if len(book['slug']) >= 3 and book['slug'] in upload['stem']:
        score += 40
    
    # 8. 上传文件名包含书名 token
    if title_tokens:
        contained = sum(1 for t in title_tokens if t in upload_tokens)
        score += (contained / len(title_tokens)) * 30
    
    return score

def match_all(books, uploads):
    """为每个上传文件找最佳匹配的书籍，返回 {upload_filename: book}
    允许多个上传文件匹配同一本书（如多卷/多格式）"""
    matches = {}
    
    for upload in uploads:
        best_book = None
        best_score = 0
        
        for book in books:
            score = match_score(book, upload)
            if score > best_score:
                best_score = score
                best_book = book
        
        # 阈值：至少要有一定匹配度
        if best_book and best_score >= 30:
            matches[upload['filename']] = best_book
    
    return matches

def extract_pdf_cover(pdf_path, output_path):
    """用 pdftoppm 提取 PDF 第一页为 JPEG"""
    try:
        # pdftoppm -f 1 -l 1 -singlefile -jpeg -scale-to 400 input.pdf output_prefix
        prefix = output_path.rsplit('.', 1)[0]
        result = subprocess.run(
            ['pdftoppm', '-f', '1', '-l', '1', '-singlefile', '-jpeg', '-scale-to', '400', pdf_path, prefix],
            capture_output=True, text=True, timeout=30
        )
        # pdftoppm 输出为 prefix.jpg
        actual = prefix + '.jpg'
        if os.path.exists(actual):
            if actual != output_path:
                shutil.move(actual, output_path)
            return True
        
        # 某些版本输出 -1.jpg
        alt = prefix + '-1.jpg'
        if os.path.exists(alt):
            shutil.move(alt, output_path)
            return True
        
        return False
    except Exception as e:
        print(f"  ⚠ PDF 封面提取错误: {e}")
        return False

def extract_epub_cover(epub_path, output_path):
    """从 EPUB（ZIP）中提取封面图片"""
    try:
        import zipfile
        
        with zipfile.ZipFile(epub_path, 'r') as zf:
            # 方法1：查找 container.xml → OPF → cover 引用
            # 方法2：直接找常见封面文件名
            cover_candidates = []
            
            for name in zf.namelist():
                lower = name.lower()
                # 常见封面路径
                if 'cover' in lower and any(lower.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                    cover_candidates.append(name)
                # 根目录封面
                if lower in ['cover.jpg', 'cover.jpeg', 'cover.png']:
                    cover_candidates.insert(0, name)  # 优先
            
            if not cover_candidates:
                # 方法3：找第一张图片
                for name in zf.namelist():
                    lower = name.lower()
                    if any(lower.endswith(ext) for ext in ['.jpg', '.jpeg', '.png']) and 'cover' not in lower:
                        # 排除小图标
                        info = zf.getinfo(name)
                        if info.file_size > 10000:  # >10KB
                            cover_candidates.append(name)
                            break
            
            if not cover_candidates:
                return False
            
            # 使用第一个候选
            cover_name = cover_candidates[0]
            data = zf.read(cover_name)
            
            with open(output_path, 'wb') as f:
                f.write(data)
            
            return True
    
    except Exception as e:
        print(f"  ⚠ EPUB 封面提取错误: {e}")
        return False

def update_frontmatter(filepath, raw_fm, body, cover_url):
    """更新 markdown 文件的 cover 字段"""
    new_raw = re.sub(
        r'^cover:\s*".*?"',
        f'cover: "{cover_url}"',
        raw_fm,
        flags=re.MULTILINE
    )
    
    new_content = f'---\n{new_raw}\n---{body}'
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

def main():
    print("=" * 60)
    print("📚 电子书匹配 + 封面提取工具")
    print("=" * 60)
    
    # 加载数据
    books = load_books()
    uploads = load_uploads()
    
    print(f"\n📖 书籍数量: {len(books)}")
    print(f"📁 上传文件数量: {len(uploads)}")
    
    # 创建 covers 目录
    os.makedirs(COVERS_DIR, exist_ok=True)
    
    # 匹配
    print("\n🔍 开始匹配...")
    matches = match_all(books, uploads)
    
    matched_books = set()
    cover_extracted = 0
    cover_skipped = 0
    cover_failed = 0
    
    results = []
    
    for upload in uploads:
        filename = upload['filename']
        if filename in matches:
            book = matches[filename]
            matched_books.add(book['slug'])
            cover_url = ''
            
            # 提取封面
            current_cover = book['data'].get('cover', '')
            has_cover = current_cover and current_cover.strip() and current_cover != '""'
            
            if has_cover:
                cover_skipped += 1
                status = '⏭ 已有封面'
                cover_url = current_cover
            else:
                cover_filename = f"{book['slug']}.jpg"
                cover_path = os.path.join(COVERS_DIR, cover_filename)
                
                success = False
                if upload['ext'] == 'pdf':
                    success = extract_pdf_cover(upload['path'], cover_path)
                elif upload['ext'] == 'epub':
                    success = extract_epub_cover(upload['path'], cover_path)
                
                if success:
                    cover_url = f"/covers/{cover_filename}"
                    update_frontmatter(book['filepath'], book['raw_fm'], book['body'], cover_url)
                    cover_extracted += 1
                    status = '✅ 封面已提取'
                else:
                    cover_failed += 1
                    status = '❌ 封面提取失败'
            
            results.append({
                'upload': filename,
                'book': book['title'],
                'slug': book['slug'],
                'status': status,
            })
            
            print(f"  {status}")
            print(f"    📁 {filename}")
            print(f"    📖 → {book['title']} ({book['slug']})")
            if cover_url:
                print(f"    🖼  {cover_url}")
        else:
            results.append({
                'upload': filename,
                'book': '—',
                'slug': '—',
                'status': '❓ 未匹配到书籍',
            })
            print(f"  ❓ 未匹配")
            print(f"    📁 {filename}")
    
    # 统计
    print("\n" + "=" * 60)
    print("📊 统计")
    print("=" * 60)
    print(f"  上传文件总数: {len(uploads)}")
    print(f"  匹配成功:     {len(matches)}")
    print(f"  未匹配:       {len(uploads) - len(matches)}")
    print(f"  封面已提取:   {cover_extracted}")
    print(f"  已有封面跳过: {cover_skipped}")
    print(f"  提取失败:     {cover_failed}")
    
    # 显示未匹配的上传文件
    unmatched = [r for r in results if '未匹配' in r['status']]
    if unmatched:
        print(f"\n⚠ 以下文件未匹配到书籍：")
        for r in unmatched:
            print(f"  📁 {r['upload']}")
    
    # 显示没有上传文件的书籍（有书名但无电子书）
    unmatched_books = [b for b in books if b['slug'] not in matched_books]
    # 只显示书名与上传文件名可能有关系的
    print(f"\n📝 已匹配 {len(matched_books)}/{len(books)} 本书")

if __name__ == '__main__':
    main()
