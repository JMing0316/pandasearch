# 🐼 PandaSearch / 胖达搜索

> Universal AI-powered search plugin for PostgreSQL.
> Configure any table with YAML, get intelligent search in 30 seconds.
>
> 通用 AI 搜索插件，任意 PostgreSQL 数据表通过 YAML 配置即可接入，30 秒上手。

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-61dafb.svg)](https://react.dev)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16+-336791.svg)](https://www.postgresql.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## ✨ 特性

- 🔌 **通用接入** — 任意 PostgreSQL 数据表，YAML 配置即可接入
- ⚡ **极简配置** — 30 秒上手：只填表名，系统自动发现所有配置
- 🔧 **基础可调** — 5 分钟：微调字段权重、搜索策略、UI 展示
- 🎛️ **高级可选** — 30 分钟（可选）：自定义模板、插件、同义词
- 🧠 **Agent 驱动** — LangGraph Agent 理解意图，动态选择检索策略
- 🔀 **混合检索** — 向量语义搜索 + 全文关键词搜索 + SQL 结构化过滤
- 👤 **个性化** — 融合用户画像、历史行为、内容动态排序
- 📊 **百万数据** — 基于现有 PostgreSQL，无需数据迁移

---

## 🚀 快速开始（30 秒接入）

```bash
# 1. 克隆仓库
git clone https://github.com/<your-username>/pandasearch.git
cd pandasearch

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 填入 OPENAI_API_KEY

# 3. 启动服务
docker-compose -f docker/docker-compose.yml up -d

# 4. 创建极简配置文件
cat > config.yaml << 'EOF'
data_source:
  table: products
EOF

# 5. 初始化（胖达自动发现 Schema、生成配置、创建索引）
docker-compose exec backend python -m pandasearch init --config config.yaml

# 6. 完成！访问 http://localhost:3000
```

**启动日志：**

```
🐼 胖达正在吃数据...
🎋 已扫描表结构
🎋 已发现 12 个字段
🎋 已推断 5 个搜索字段、3 个过滤字段
🎋 已生成默认配置
♨️  正在构建向量索引...
✅ 向量索引构建完成（HNSW m=16, ef=64）
✅ 全文索引构建完成（GIN）
🐼 胖达吃饱了！已吃下 1,000,000 条记录
🐼 访问 http://localhost:3000 开始搜索
```

---

## 📖 文档

| 文档 | 说明 |
|------|------|
| [📄 配置指南](docs/CONFIG_GUIDE.md) | 从 30 秒极简到 30 分钟高级配置 |
| [📄 API 文档](docs/API_REFERENCE.md) | RESTful API 参考 |
| [📄 部署指南](docs/DEPLOYMENT.md) | Docker / K8s 部署方案 |
| [📄 技术方案](docs/SPEC.md) | 完整 MVP 架构设计 |
| [📄 贡献指南](CONTRIBUTING.md) | 如何参与贡献 |
| [📄 变更日志](CHANGELOG.md) | 版本变更记录 |

---

## 🏗️ 架构

```
用户 → React搜索框 → FastAPI → LangGraph Agent → 并行检索 → RRF融合 → 个性化排序 → SSE流式返回
                                          ↓
                              PostgreSQL + pgvector (HNSW) + GIN全文索引
                                          ↓
                                   Redis 缓存层
```

**五层配置模型：**

```
Layer 5: 行为配置（防抖、分页、排序）
Layer 4: 展示模板（卡片布局、字段顺序）
Layer 3: 检索策略（向量/全文/SQL权重、RRF）
Layer 2: 字段映射（搜索/过滤/权重/Embedding策略）
Layer 1: 数据源（表名、连接、Schema发现）
```

---

## 📁 项目结构

```
pandasearch/
├── 🐼 backend/pandasearch/           # Python 后端
│   ├── config.py                     # 五层配置模型
│   ├── schema_discovery.py           # Schema 自动发现
│   ├── field_classifier.py           # 字段分类引擎
│   ├── embedding.py                  # 动态 Embedding 生成
│   ├── search_engine.py              # 通用检索引擎
│   ├── agent/                        # LangGraph Agent
│   │   ├── graph.py                  # 状态机定义
│   │   ├── nodes/                    # Agent 节点
│   │   │   ├── query_analysis.py
│   │   │   ├── intent_classify.py
│   │   │   ├── parallel_search.py
│   │   │   ├── rerank.py
│   │   │   └── response_gen.py
│   │   └── tools/                    # Agent 工具
│   │       ├── vector_search.py
│   │       ├── fulltext_search.py
│   │       └── sql_filter.py
│   └── templates/                    # Embedding 模板
│       ├── ecommerce.yaml
│       ├── article.yaml
│       └── default.yaml
├── 🎨 frontend/pandasearch-ui/       # React 前端
│   └── src/components/               # 搜索组件
│       ├── SearchBox/                # 搜索框 + 自动补全
│       ├── FilterPanel/              # 筛选器面板
│       ├── ResultList/               # 结果列表
│       ├── ResultCard/               # 结果卡片（配置驱动）
│       ├── AISummary/                # AI 推荐语
│       └── ...
├── ⚙️ configs/                       # 配置模板
│   ├── minimal.yaml                  # 极简配置（30秒）
│   ├── basic.yaml                    # 基础配置（5分钟）
│   └── advanced.yaml                 # 高级配置（30分钟）
├── 📚 examples/                      # 使用示例
├── 🐳 docker/                        # Docker 配置
│   └── docker-compose.yml
└── 📖 docs/                          # 文档
```

---

## 🛠️ 技术栈

| 层级 | 技术 | 版本 |
|------|------|------|
| 前端 | React + TypeScript + Tailwind CSS | 18+ / 5.5+ / 3.4+ |
| 后端 | FastAPI (async) | 0.115+ |
| Agent | LangGraph + LangChain | 0.2+ / 0.3+ |
| 数据库 | PostgreSQL + pgvector | 16+ / 0.7+ |
| 缓存 | Redis | 7+ |
| Embedding | OpenAI API | text-embedding-3-small |
| LLM | OpenAI API | GPT-4o-mini |
| 部署 | Docker Compose | - |

---

## 🤝 贡献

欢迎贡献！请阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 了解如何参与。

## 📄 许可证

[MIT License](LICENSE) © PandaSearch Team

---

> 🐼 胖达搜索 — 让每一张数据表都拥有 AI 智能搜索能力
