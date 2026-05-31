import { defineCollection, z } from 'astro:content';

// 📚 书籍收藏
const books = defineCollection({
  schema: z.object({
    title: z.string(),
    originalTitle: z.string().optional(), // 原版书名（中文书留空）
    author: z.string(),
    cover: z.string(),                    // 封面图片路径
    rating: z.number().min(0).max(10),    // 评分 0-10，显示时换算为 5 星
    readingStart: z.date(),               // 开始阅读日期
    readingEnd: z.date().optional(),      // 结束阅读日期
    status: z.enum(['已读', '在读', '想读']),
    tags: z.array(z.string()).default([]),
    isbn: z.string().optional(),
    publisher: z.string().optional(),
    publishedYear: z.number().optional(),
    pages: z.number().optional(),
    summary: z.string().optional(),       // 简短摘要，显示在卡片上
    draft: z.boolean().default(false),
  }),
});

// 🎬 影视收藏
const movies = defineCollection({
  schema: z.object({
    title: z.string(),
    originalTitle: z.string().optional(), // 原片名
    director: z.string().optional(),
    poster: z.string(),                   // 海报图片路径
    rating: z.number().min(0).max(10),
    bgmid: z.number().optional(),          // Bangumi 条目 ID
    watchDate: z.date(),                  // 观看日期
    year: z.number(),                     // 上映年份
    type: z.enum(['电影', '剧集', '纪录片', '动画']),
    tags: z.array(z.string()).default([]),
    summary: z.string().optional(),
    draft: z.boolean().default(false),
  }),
});

// 🎮 游戏收藏
const games = defineCollection({
  schema: z.object({
    title: z.string(),
    originalTitle: z.string().optional(), // 原版名称
    developer: z.string().optional(),      // 开发商
    poster: z.string(),                    // 封面图片路径
    rating: z.number().min(0).max(10),
    bgmid: z.number().optional(),          // Bangumi 条目 ID
    playDate: z.date(),                    // 开始游玩日期
    year: z.number(),                      // 发行年份
    platform: z.enum(['PC', 'Switch', 'PS5', 'Xbox', 'iOS', 'Android', '多平台', '其他']),
    tags: z.array(z.string()).default([]),
    summary: z.string().optional(),
    draft: z.boolean().default(false),
  }),
});

// 📝 日记
const diary = defineCollection({
  schema: z.object({
    title: z.string(),
    date: z.date(),
    mood: z.enum(['😊', '😌', '😐', '😢', '😡', '🤩']).optional(),
    weather: z.string().optional(),
    tags: z.array(z.string()).default([]),
    draft: z.boolean().default(false),
  }),
});

export const collections = { books, movies, games, diary };
