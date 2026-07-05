# LogFast — AI 更新日志生成器

> 再也不用手动写更新日志了。LogFast 读取你的 Git 提交记录，用 AI 理解变更内容，秒级生成用户友好的更新日志（changelog）。

## 技术栈

| 层 | 技术 |
|-------|------|
| 前端 | Vue 3 + Vite + TailwindCSS |
| 后端 | Python FastAPI |
| 数据库 | PostgreSQL（通过 Supabase / asyncpg） |
| AI | DeepSeek / OpenAI 兼容 API |
| 认证 | GitHub OAuth |
| 支付 | Lemon Squeezy |

## 快速开始

### 1. 后端

```bash
cd backend
cp .env.example .env   # 编辑 GitHub OAuth + AI API 密钥
pip install -r requirements.txt
python run.py           # 启动 http://localhost:8000
```

### 2. 前端

```bash
cd frontend
npm install
npm run dev             # 启动 http://localhost:5173
```

### 3. 数据库

```bash
# 推荐使用 Supabase：
# 设置 DATABASE_URL 为 Supabase PostgreSQL 连接串
# 表会在首次运行时自动创建

# 或本地 PostgreSQL：
createdb logfast
# 在 .env 中更新 DATABASE_URL
```

## GitHub OAuth 设置

1. 前往 https://github.com/settings/developers
2. 创建新的 OAuth App
3. 回调 URL 设为：`http://localhost:8000/api/auth/github/callback`
4. 复制 Client ID 和 Secret 到 `.env`

## AI API 设置

从 [DeepSeek](https://platform.deepseek.com/) 或任何 OpenAI 兼容服务商获取 API 密钥，在 `.env` 中设置 `AI_API_KEY`。

## 项目结构

```
logfast/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI 入口
│   │   ├── config.py        # 环境配置
│   │   ├── models.py        # SQLAlchemy 模型
│   │   ├── database.py      # 数据库连接
│   │   ├── routes/
│   │   │   ├── auth.py      # GitHub OAuth
│   │   │   ├── changelog.py # 仓库 + changelog CRUD
│   │   │   └── webhook.py   # GitHub push webhook
│   │   └── services/
│   │       ├── github.py    # GitHub API 客户端
│   │       └── ai.py        # AI changelog 生成
│   ├── run.py
│   ├── requirements.txt
│   └── Dockerfile
└── frontend/
    ├── src/
    │   ├── App.vue
    │   ├── views/
    │   │   ├── LandingPage.vue
    │   │   ├── AuthCallback.vue
    │   │   ├── Dashboard.vue
    │   │   ├── ChangelogPage.vue
    │   │   └── PublicChangelog.vue
    │   └── stores/
    │       ├── auth.js
    │       └── repos.js
    ├── index.html
    ├── vite.config.js
    └── vercel.json
```

## MVP 功能清单

- [x] GitHub OAuth 登录
- [x] 列出仓库 + 连接/断开
- [x] 从已连接仓库获取提交记录
- [x] AI 生成更新日志（DeepSeek）
- [x] 草稿/发布流程
- [x] 公开更新日志页面（`/p/:owner/:repo`）
- [x] GitHub push webhook（自动生成）
- [ ] 邮件订阅通知
- [ ] 内嵌组件（Embed Widget）
- [ ] 自定义域名
- [ ] Gitee / Coding.net 支持
- [ ] 中文界面
- [ ] Lemon Squeezy 支付集成
