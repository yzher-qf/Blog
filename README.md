# 📖 Yzher's Blog — 个人博客

基于 [Astro 5](https://astro.build) 的个人阅读/观影/游戏/日记博客，部署在腾讯云服务器上。

## 技术栈

| 层面 | 技术 |
|------|------|
| 框架 | Astro 5 (SSR 模式) |
| 前端交互 | Vue 3 (星级评分组件) |
| 样式 | Tailwind CSS 3 |
| 内容管理 | Astro Content Collections |
| 封面获取 | Open Library (书籍) / Bangumi (影视&游戏) |
| 反向代理 | Nginx |
| 网盘 | Alist (systemd 管理) |

## 项目结构

```
my-blog/
├── astro.config.mjs          # Astro 配置 (SSR, 端口 4321, Vue+Tailwind)
├── package.json              # 依赖与脚本
├── tailwind.config.mjs       # Tailwind 配置
├── tsconfig.json
├── .gitignore                # 忽略 node_modules, dist, .astro, public/uploads/
├── public/
│   ├── favicon.svg
│   └── uploads/              # 电子书存放目录（不入 git）
└── src/
    ├── content/
    │   ├── config.ts         # Content Collections schema（书籍/影视/游戏/日记）
    │   ├── books/            # 书籍 markdown
    │   ├── movies/           # 影视 markdown
    │   ├── games/            # 游戏 markdown
    │   └── diary/            # 日记 markdown
    ├── pages/
    │   ├── index.astro       # 首页（横滚卡片展示最近在读/在看/在玩）
    │   ├── books/
    │   │   ├── index.astro   # 书架列表（瀑布流 + 排序/筛选/标签）
    │   │   └── [slug].astro  # 书籍详情（含下载按钮）
    │   ├── movies/
    │   │   ├── index.astro
    │   │   └── [slug].astro
    │   ├── games/
    │   │   ├── index.astro
    │   │   └── [slug].astro
    │   └── diary/
    │       ├── index.astro
    │       └── [slug].astro
    ├── components/
    │   ├── BookCard.astro    # 书籍卡片（封面占位/可点击标签）
    │   ├── MovieCard.astro
    │   ├── GameCard.astro
    │   ├── DiaryCard.astro
    │   ├── Header.astro      # 导航栏（含 alist 网盘入口）
    │   ├── Footer.astro
    │   └── StarRating.vue    # Vue 星级评分组件
    ├── layouts/
    │   └── BaseLayout.astro  # 基础布局
    └── styles/
        └── global.css        # 全局样式（瀑布流/网格布局）
```

## 关键特性

### 1. SSR 模式
`astro.config.mjs` 中 `output: 'server'`，筛选/排序通过 URL 参数实现服务端渲染：
- `/books?sort=title` — 书名排序
- `/books?status=想读` — 状态筛选
- `/books?tag=科幻` — 标签筛选
- 参数可组合：`/books?sort=title&status=想读&tag=小说`

### 2. 书籍内容结构
每本书 `src/content/books/*.md` 的 frontmatter：
```yaml
title: "三国演义"
author: "罗贯中"
cover: ""              # 有则填写 URL，无则显示占位卡片
rating: 0              # 0-5
readingStart: 2026-05-31
status: "想读"         # 已读 | 在读 | 想读
tags: ["中国文学", "古典", "小说"]
summary: "《三国演义》—— 罗贯中 著。"
```

### 3. 电子书下载
- 书籍详情页底部有下载区域
- 将文件命名为 `{书名slug}.{格式}` 放入 `public/uploads/`
- 支持格式：epub, pdf, mobi, azw3, txt
- 文件名示例：`public/uploads/三国演义.epub`
- `public/uploads/` 已加入 `.gitignore`，不纳入版本控制

### 4. 封面占位
无 `cover` 的书籍自动显示 📖 + 书名 + 作者的占位卡片

### 5. 标签系统
- 书籍卡片上的标签可点击，跳转到 `/books?tag=xxx`
- 书架页面顶部有 Top 20 标签快捷筛选

### 6. 游戏记录
仿照影视的 Schema，支持平台分类：PC / Switch / PS5 / Xbox / iOS / Android / 多平台 / 其他

### 7. 封面自动匹配

| 内容 | 来源 | 脚本 |
|------|------|------|
| 📚 书籍 | Open Library API | `fetch_covers.py`* |
| 🎬 影视 | Bangumi (bgm.tv) | `fetch_bangumi_covers.py` |
| 🎮 游戏 | Bangumi (bgm.tv) | `fetch_bangumi_covers.py` |

\* Open Library 中文书覆盖率有限，建议手动填写封面 URL 或从 PDF/EPUB 提取（`match_and_covers.py`）

## 常用命令

```bash
# 开发
cd /root/my-blog
npm run dev          # 启动开发服务器 (localhost:4321)

# Git 同步
git add -A && git commit -m "xxx"
git push              # 推送至 GitHub

# 服务器拉取
cd /root/my-blog && git pull   # Astro 自动热更新
```

> `public/uploads/` 和 `public/covers/` 已加入 `.gitignore`，不同步到 GitHub，仅服务器本地保留。

## 服务器部署

### Nginx 配置
配置文件：`/etc/nginx/conf.d/yzher.conf`

```
域名 yzher.xyz → Nginx :80
  ├── /alist  → localhost:5244 (Alist)
  └── /*      → localhost:4321 (Astro)
```

### Alist
- 安装路径：`/opt/alist/`
- 服务管理：`systemctl {start|stop|restart} alist`
- 开机自启：已启用
- 账号：`yzher` / `yzh20020313`
- 配置文件：`/opt/alist/data/config.json` (`site_url: "/alist"`)

### 进程管理
```bash
# Astro 开发服务器
pkill -f "astro dev"
cd /root/my-blog && npm run dev

# Nginx
nginx -s reload
nginx -t              # 测试配置

# Alist
systemctl restart alist
```

## 书籍 Schema 参考

| 字段 | 类型 | 必填 | 说明 |
|------|------|:--:|------|
| title | string | ✅ | 书名 |
| author | string | ✅ | 作者 |
| cover | string | ✅ | 封面 URL，空字符串则显示占位 |
| rating | number 0-5 | ✅ | 评分，未读填 0 |
| readingStart | date | ✅ | 开始阅读日期 |
| readingEnd | date | ❌ | 结束阅读日期 |
| status | enum | ✅ | `已读` / `在读` / `想读` |
| tags | string[] | ❌ | 标签数组 |
| summary | string | ❌ | 摘要 |
| draft | boolean | ❌ | 草稿，true 则隐藏 |

## 游戏 Schema 参考

| 字段 | 类型 | 必填 | 说明 |
|------|------|:--:|------|
| title | string | ✅ | 游戏名 |
| originalTitle | string | ❌ | 原版名称 |
| developer | string | ❌ | 开发商 |
| poster | string | ✅ | 封面 URL，空字符串则显示占位 |
| rating | number 0-5 | ✅ | 评分 |
| playDate | date | ✅ | 开始游玩日期 |
| year | number | ✅ | 发行年份 |
| platform | enum | ✅ | PC / Switch / PS5 / Xbox / iOS / Android / 多平台 / 其他 |
| tags | string[] | ❌ | 标签数组 |
| summary | string | ❌ | 摘要 |
| draft | boolean | ❌ | 草稿 |
