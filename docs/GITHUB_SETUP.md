# PandaSearch — GitHub 仓库创建指南

> 项目名：PandaSearch | 文件夹名：pandasearch | 中文：胖达搜索

---

## 目录

1. [创建 GitHub 仓库](#一创建-github-仓库)
2. [本地项目初始化](#二本地项目初始化)
3. [项目目录结构](#三项目目录结构)
4. [初始文件模板](#四初始文件模板)
5. [首次推送代码](#五首次推送代码)
6. [分支策略](#六分支策略)
7. [环境变量配置](#七环境变量配置)
8. [协作者设置](#八协作者设置)
9. [GitHub Actions CI/CD](#九github-actions-cicd-可选)
10. [标签与版本管理](#十标签与版本管理)

---

## 一、创建 GitHub 仓库

### 方式 A：GitHub Web 界面（推荐）

1. 打开 https://github.com/new
2. 填写仓库信息：

| 字段 | 填写内容 |
|------|---------|
| **Repository name** | `pandasearch` |
| **Description** | `🐼 PandaSearch — Universal AI-powered search plugin for PostgreSQL. Configure any table with YAML, get intelligent search in 30 seconds.` |
| **Visibility** | `Public` （推荐开源）或 `Private` |
| **Add a README** | ✅ 勾选 |
| **Add .gitignore** | 选择 `Python` |
| **Choose a license** | 选择 `MIT License` |

3. 点击 **Create repository**

### 方式 B：GitHub CLI

```bash
# 安装 GitHub CLI（如未安装）
# macOS: brew install gh
# Ubuntu: sudo apt install gh
# 登录
gh auth login

# 创建仓库
gh repo create pandasearch \
  --description "🐼 PandaSearch — Universal AI-powered search plugin for PostgreSQL" \
  --public \
  --add-readme \
  --gitignore Python \
  --license MIT

# 克隆到本地
gh repo clone <your-username>/pandasearch
cd pandasearch
```

---

## 二、本地项目初始化

### 2.1 如果是从零开始

```bash
# 1. 创建项目目录
mkdir pandasearch
cd pandasearch

# 2. 初始化 Git
git init

# 3. 添加远程仓库（替换 <your-username>）
git remote add origin https://github.com/<your-username>/pandasearch.git

# 4. 创建目录结构
mkdir -p backend/pandasearch frontend/pandasearch-ui configs examples docs docker

# 5. 创建初始文件
touch README.md .gitignore LICENSE backend/requirements.txt frontend/package.json configs/example.yaml docker/docker-compose.yml
```

### 2.2 如果已克隆 GitHub 生成的仓库

```bash
cd pandasearch

# 创建目录结构
mkdir -p backend/pandasearch frontend/pandasearch-ui configs examples docs docker
```

---

## 三、项目目录结构

```
pandasearch/                          # Git 仓库根目录
│
├── 📄 README.md                      # 项目主文档
├── 📄 LICENSE                        # MIT 许可证
├── 📄 .gitignore                     # Git 忽略规则
├── 📄 .env.example                   # 环境变量模板（不含敏感值）
├── 📄 CONTRIBUTING.md                # 贡献指南
├── 📄 CHANGELOG.md                   # 版本变更记录
│
├── 🐼 backend/                       # Python 后端
│   ├── pandasearch/                  # Python 包
│   │   ├── __init__.py               # 包入口
│   │   ├── main.py                   # FastAPI 应用入口
│   │   ├── config.py                 # 配置管理（五层配置模型）
│   │   ├── schema_discovery.py       # Schema 自动发现服务
│   │   ├── field_classifier.py       # 字段分类引擎（15条规则）
│   │   ├── embedding.py              # 动态 Embedding 生成
│   │   ├── search_engine.py          # 通用检索引擎
│   │   ├── agent/                    # LangGraph Agent
│   │   │   ├── __init__.py
│   │   │   ├── graph.py              # Agent 状态机定义
│   │   │   ├── nodes/                # Agent 节点
│   │   │   │   ├── query_analysis.py
│   │   │   │   ├── intent_classify.py
│   │   │   │   ├── route_select.py
│   │   │   │   ├── parallel_search.py
│   │   │   │   ├── rerank.py
│   │   │   │   └── response_gen.py
│   │   │   └── tools/                # Agent 工具
│   │   │       ├── vector_search.py
│   │   │       ├── fulltext_search.py
│   │   │       └── sql_filter.py
│   │   ├── database.py               # PostgreSQL 连接管理
│   │   ├── cache.py                  # Redis 缓存管理
│   │   ├── templates/                # Embedding 模板
│   │   │   ├── ecommerce.yaml
│   │   │   ├── article.yaml
│   │   │   ├── knowledge_base.yaml
│   │   │   ├── user_profile.yaml
│   │   │   └── default.yaml
│   │   └── utils/
│   │       ├── logger.py
│   │       └── security.py           # SQL 注入防护
│   ├── requirements.txt              # Python 依赖
│   ├── requirements-dev.txt          # 开发依赖
│   ├── pyproject.toml                # 现代 Python 项目配置
│   ├── Dockerfile                    # 后端 Docker 镜像
│   └── tests/                        # 测试
│       ├── test_schema_discovery.py
│       ├── test_search_engine.py
│       └── test_agent.py
│
├── 🎨 frontend/                      # React 前端
│   ├── pandasearch-ui/               # React 应用
│   │   ├── public/
│   │   ├── src/
│   │   │   ├── App.tsx
│   │   │   ├── main.tsx
│   │   │   ├── components/           # 搜索组件
│   │   │   │   ├── SearchBox/
│   │   │   │   ├── FilterPanel/
│   │   │   │   ├── ResultList/
│   │   │   │   ├── ResultCard/
│   │   │   │   ├── SortBar/
│   │   │   │   ├── Pagination/
│   │   │   │   ├── AISummary/
│   │   │   │   └── EmptyState/
│   │   │   ├── hooks/                # 自定义 Hooks
│   │   │   │   ├── useSearch.ts
│   │   │   │   ├── useSuggest.ts
│   │   │   │   └── useConfig.ts
│   │   │   ├── types/                # TypeScript 类型
│   │   │   │   └── index.ts
│   │   │   └── services/             # API 调用层
│   │   │       └── api.ts
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   ├── tailwind.config.js
│   │   ├── vite.config.ts
│   │   └── Dockerfile
│   └── README.md
│
├── ⚙️ configs/                       # 配置模板
│   ├── example.yaml                  # 完整示例配置
│   ├── minimal.yaml                  # 极简配置（30秒）
│   ├── basic.yaml                    # 基础配置（5分钟）
│   └── advanced.yaml                 # 高级配置（30分钟）
│
├── 📚 examples/                      # 使用示例
│   ├── ecommerce_products.yaml       # 电商商品搜索示例
│   ├── blog_articles.yaml            # 文章搜索示例
│   └── user_profiles.yaml            # 用户搜索示例
│
├── 🐳 docker/                        # Docker 配置
│   ├── docker-compose.yml            # 主编排文件
│   ├── docker-compose.dev.yml        # 开发环境
│   ├── docker-compose.prod.yml       # 生产环境
│   └── init/                         # 初始化脚本
│       ├── 01_init_db.sql
│       └── 02_seed_data.sql
│
├── 📖 docs/                          # 文档
│   ├── SPEC.md                       # MVP 技术方案
│   ├── CONFIG_GUIDE.md               # 配置指南（替代可视化界面）
│   ├── API_REFERENCE.md              # API 文档
│   ├── DEPLOYMENT.md                 # 部署指南
│   └── ARCHITECTURE.md               # 架构文档
│
└── 📋 history/                       # 历史版本
    └── architecture_proposal_v1.md   # v1.0 原始架构
```

---

## 四、初始文件模板

### 4.1 README.md（项目主文档）

```markdown
# 🐼 PandaSearch / 胖达搜索

> Universal AI-powered search plugin for PostgreSQL.  
> Configure any table with YAML, get intelligent search in 30 seconds.  
> 通用 AI 搜索插件，任意 PostgreSQL 数据表通过 YAML 配置即可接入，30 秒上手。

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-61dafb.svg)](https://react.dev)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16+-336791.svg)](https://www.postgresql.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ 特性

- 🔌 **通用接入** — 任意 PostgreSQL 数据表，YAML 配置即可接入
- ⚡ **极简配置** — 30 秒上手：只填表名，系统自动发现所有配置
- 🔧 **基础可调** — 5 分钟：微调字段权重、搜索策略、UI 展示
- 🧠 **Agent 驱动** — LangGraph Agent 理解意图，动态选择检索策略
- 🔀 **混合检索** — 向量语义搜索 + 全文关键词搜索 + SQL 结构化过滤
- 👤 **个性化** — 融合用户画像、历史行为、内容动态排序
- 📊 **百万数据** — 基于现有 PostgreSQL，无需数据迁移

## 🚀 快速开始（30 秒接入）

```bash
# 1. 克隆仓库
git clone https://github.com/<your-username>/pandasearch.git
cd pandasearch

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 填入 OPENAI_API_KEY

# 3. 启动服务
docker-compose up -d

# 4. 创建极简配置文件
cat > config.yaml << 'EOF'
data_source:
  table: products
EOF

# 5. 初始化（胖达自动发现 Schema、生成配置、创建索引）
docker-compose exec backend python -m pandasearch init --config config.yaml

# 6. 完成！访问 http://localhost:3000
```

🐼 胖达正在吃数据...  
🎋 已吃下 1,000,000 条记录  
✅ 向量索引构建完成  
✅ 全文索引构建完成  
🐼 胖达吃饱了！访问 http://localhost:3000 开始搜索

## 📖 文档

- [配置指南](docs/CONFIG_GUIDE.md) — 从 30 秒极简到 30 分钟高级配置
- [API 文档](docs/API_REFERENCE.md) — RESTful API 参考
- [部署指南](docs/DEPLOYMENT.md) — Docker / K8s 部署
- [技术方案](docs/SPEC.md) — 完整 MVP 架构设计

## 🏗️ 架构

```
用户 → React搜索框 → FastAPI → LangGraph Agent → 并行检索 → RRF融合 → 个性化排序 → SSE流式返回
                                          ↓
                              PostgreSQL + pgvector (HNSW) + GIN全文索引
                                          ↓
                                   Redis 缓存层
```

## 📄 许可证

[MIT License](LICENSE) © PandaSearch Team
```

### 4.2 .gitignore

```gitignore
# === Python ===
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# === Virtual Environments ===
venv/
env/
ENV/
.venv/

# === IDEs ===
.idea/
.vscode/
*.swp
*.swo
*~
.DS_Store

# === Environment Variables ===
.env
.env.local
.env.*.local

# === Database ===
*.db
*.sqlite
*.sqlite3

# === Logs ===
*.log
logs/

# === Test Coverage ===
.coverage
htmlcov/
.pytest_cache/
.mypy_cache/

# === Node.js / React ===
node_modules/
*.lock
package-lock.json
yarn.lock
.pnpm-debug.log*

# === Build Output ===
frontend/pandasearch-ui/dist/
frontend/pandasearch-ui/build/

# === Docker Volumes ===
volumes/
postgres_data/
redis_data/

# === OS ===
Thumbs.db
```

### 4.3 .env.example（环境变量模板）

```bash
# ============================================
# PandaSearch 环境变量模板
# 复制为 .env 后填入实际值
# ============================================

# --- OpenAI API ---
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1

# --- 数据库 ---
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/pandasearch
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

# --- Redis ---
REDIS_URL=redis://redis:6379/0
REDIS_POOL_SIZE=50

# --- 应用配置 ---
APP_ENV=development
APP_DEBUG=true
APP_LOG_LEVEL=INFO
SECRET_KEY=change-this-to-a-random-secret-key

# --- 搜索配置 ---
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100
CACHE_TTL_SECONDS=300

# --- 监控（可选）---
SENTRY_DSN=
```

### 4.4 CONTRIBUTING.md（贡献指南）

```markdown
# 贡献指南

感谢您对 PandaSearch（胖达搜索）的兴趣！

## 开发环境搭建

```bash
# 1. 克隆仓库
git clone https://github.com/<your-username>/pandasearch.git
cd pandasearch

# 2. 启动开发环境
docker-compose -f docker/docker-compose.dev.yml up -d

# 3. 安装 Python 依赖
cd backend
pip install -r requirements-dev.txt

# 4. 安装前端依赖
cd ../frontend/pandasearch-ui
npm install
```

## 分支策略

- `main` — 稳定分支，通过 CI 后才能合并
- `dev` — 开发分支，日常开发基于此
- `feature/*` — 功能分支
- `bugfix/*` — 修复分支

## 提交规范

```
feat: 新功能
fix: 修复问题
docs: 文档更新
style: 代码格式（不影响功能）
refactor: 重构
test: 测试相关
chore: 构建/工具相关
```
```

### 4.5 CHANGELOG.md（版本记录）

```markdown
# 变更日志

所有 notable 变更都将记录在此文件。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [SemVer](https://semver.org/lang/zh-CN/)。

## [Unreleased]

## [0.1.0] - 2026-06-XX

### 新增
- 通用化配置层（五层配置模型）
- Schema 自动发现服务
- 字段分类引擎（15 条规则）
- LangGraph Agent 搜索编排
- 混合检索（向量 + 全文 + SQL）
- RRF 结果融合
- React 前端搜索组件
- Docker Compose 部署
```

---

## 五、首次推送代码

```bash
# 进入项目目录
cd pandasearch

# 检查远程仓库
git remote -v
# 应显示：origin  https://github.com/<your-username>/pandasearch.git

# 添加所有文件
git add .

# 提交初始代码
git commit -m "🐼 init: PandaSearch 项目初始化

- 添加项目目录结构
- 添加 README、LICENSE、.gitignore
- 添加后端 FastAPI 项目骨架
- 添加前端 React 项目骨架
- 添加 Docker Compose 配置
- 添加配置模板和示例

胖达出生了！"

# 推送到 GitHub
git push -u origin main

# 验证推送成功
git log --oneline
# 应显示提交记录

# 在浏览器中查看
git remote get-url origin
# 打开显示的 URL 查看仓库
```

---

## 六、分支策略

### 6.1 推荐分支模型：Git Flow 简化版

```
main (稳定分支，仅合并已测试的代码)
 │
 ├── dev (开发分支，日常开发基于此)
 │    │
 │    ├── feature/schema-discovery  ← 新功能分支
 │    │      │
 │    │      └── PR → dev → main
 │    │
 │    ├── feature/search-agent
 │    │
 │    ├── feature/config-ui
 │    │
 │    └── bugfix/cache-ttl
 │
 └── release/v0.1.0  (发布分支)
```

### 6.2 分支操作命令

```bash
# 创建并切换到 dev 分支
git checkout -b dev

# 推送 dev 分支到远程
git push -u origin dev

# 创建功能分支（从 dev）
git checkout dev
git pull origin dev
git checkout -b feature/schema-discovery

# 完成功能，提交 PR
git add .
git commit -m "feat: add Schema auto-discovery service"
git push -u origin feature/schema-discovery
# 然后在 GitHub 上创建 Pull Request → dev

# 发布版本
git checkout main
git pull origin main
git checkout -b release/v0.1.0
# 更新版本号、CHANGELOG
git add .
git commit -m "chore: release v0.1.0"
git push origin release/v0.1.0
```

---

## 七、环境变量配置

### 7.1 本地开发环境

```bash
# 复制模板文件
cp .env.example .env

# 编辑 .env 填入实际值
# 必须填写：
# - OPENAI_API_KEY
# - DATABASE_URL（如果使用外部数据库）
# - SECRET_KEY（修改为随机字符串）
```

> ⚠️ **重要**：`.env` 文件已在 `.gitignore` 中，永远不会被推送到 GitHub。

### 7.2 GitHub Secrets（CI/CD 用）

在仓库设置中添加以下 Secrets：

| Secret Name | 说明 |
|-------------|------|
| `OPENAI_API_KEY` | OpenAI API 密钥 |
| `DOCKER_USERNAME` | Docker Hub 用户名 |
| `DOCKER_PASSWORD` | Docker Hub 密码 |

操作路径：**Settings → Secrets and variables → Actions → New repository secret**

---

## 八、协作者设置

### 8.1 邀请协作者

**路径**：Settings → Collaborators → Add people

| 角色 | 权限 | 适用对象 |
|------|------|---------|
| **Admin** | 完全控制 | 核心维护者 |
| **Write** | 推送代码、创建 PR | 主要开发者 |
| **Triage** | 管理 Issues 和 PR | 社区贡献者 |
| **Read** | 只读 | 外部观察者 |

### 8.2 保护分支（重要）

**路径**：Settings → Branches → Add branch protection rule

对 `main` 分支设置：
- ✅ Require a pull request before merging（必须通过 PR 合并）
- ✅ Require approvals（至少 1 人审批）
- ✅ Require status checks to pass（CI 必须通过）
- ✅ Restrict pushes that create files larger than 100MB（限制大文件）

---

## 九、GitHub Actions CI/CD（可选）

创建文件：`.github/workflows/ci.yml`

```yaml
name: CI

on:
  push:
    branches: [ main, dev ]
  pull_request:
    branches: [ main, dev ]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements-dev.txt
      - name: Run tests
        run: |
          cd backend
          pytest tests/ --cov=pandasearch --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v4

  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      - name: Install dependencies
        run: |
          cd frontend/pandasearch-ui
          npm ci
      - name: Build
        run: |
          cd frontend/pandasearch-ui
          npm run build
```

---

## 十、标签与版本管理

### 10.1 创建版本标签

```bash
# 创建标签
git tag -a v0.1.0 -m "🐼 PandaSearch v0.1.0 - MVP 发布"

# 推送标签到 GitHub
git push origin v0.1.0

# 查看所有标签
git tag -l
```

### 10.2 GitHub Release

推送标签后，在 GitHub 上：
1. 进入 **Releases** 页面
2. 点击 **Draft a new release**
3. 选择刚才推送的标签 `v0.1.0`
4. 填写 Release Notes（可以从 CHANGELOG.md 复制）
5. 点击 **Publish release**

---

## ✅ GitHub 仓库设置检查清单

| 步骤 | 状态 |
|------|------|
| 仓库创建完成 | ☐ |
| README.md 完善 | ☐ |
| .gitignore 配置 | ☐ |
| .env.example 添加 | ☐ |
| LICENSE 文件 | ☐ |
| CONTRIBUTING.md | ☐ |
| CHANGELOG.md | ☐ |
| 首次代码推送 | ☐ |
| dev 分支创建 | ☐ |
| 分支保护规则设置 | ☐ |
| GitHub Secrets 配置 | ☐ |
| 协作者邀请 | ☐ |
| GitHub Actions 配置（可选）| ☐ |

---

*🐼 胖达已准备好安家 GitHub！*
