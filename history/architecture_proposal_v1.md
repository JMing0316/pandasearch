# AI 智能搜索插件 — 架构方案

> 版本: v1.0 | 日期: 2026-06-09
> 基于 10 维度深度研究 + 交叉验证

---

## 一、项目目标

为 PostgreSQL 百万级数据构建 **AI 驱动的智能搜索插件**，核心特性：

| 特性 | 说明 |
|------|------|
| 🔍 AI 搜索框 | 电商风格的搜索框，支持自然语言查询、自动补全 |
| 🧠 Agent 驱动 | LangGraph Agent 理解意图，动态选择检索策略 |
| 🔀 混合检索 | 向量语义搜索 + 全文关键词搜索 + SQL 结构化过滤 |
| 👤 个性化 | 融合用户画像、历史行为、商品内容动态排序 |
| 📊 百万数据 | 基于现有 PostgreSQL 数据，无需迁移 |

---

## 二、系统架构图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              前端层 (React)                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │
│  │  搜索框组件   │  │  自动补全    │  │  筛选器栏    │  │  结果列表    │ │
│  │  (Autocomplete)│  │  (Suggestions)│  │  (Filters)   │  │  (Results)  │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬────┘ │
│         └─────────────────┴─────────────────┴─────────────────┘       │
│                                   │                                    │
│                            SSE 流式响应                                │
└───────────────────────────────────┬─────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼─────────────────────────────────────┐
│                         API 网关层 (FastAPI)                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │
│  │  /search       │  │  /suggest    │  │  /filters    │  │  /health    │ │
│  │  (POST)        │  │  (GET)       │  │  (GET)       │  │  (GET)      │ │
│  └──────┬───────┘  └──────────────┘  └──────────────┘  └─────────────┘ │
│         │                                                              │
│         └──────────────────────┬───────────────────────────────────────┘
│                                │
└────────────────────────────────┼────────────────────────────────────────┘
                                 │
┌────────────────────────────────▼────────────────────────────────────────┐
│                    AI Agent 编排层 (LangGraph)                             │
│                                                                          │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐        │
│   │ 1.Query  │───→│ 2.Intent │───→│ 3.Route  │───→│ 4.Search │        │
│   │ Analysis │    │ Classification│    │ Selection│    │ Execution│        │
│   └──────────┘    └──────────┘    └──────────┘    └────┬─────┘        │
│         ▲                                              │                │
│         │           ┌──────────┐    ┌──────────┐       │                │
│         └───────────│ 7.Feedback│←───│ 5.Rerank │←──────┘                │
│                     │  Loop    │    │ & Format │                        │
│                     └──────────┘    └────┬─────┘                        │
│                                          │                               │
│                     ┌────────────────────┘                               │
│                     │                                                    │
│                     ▼                                                    │
│              ┌──────────────┐                                           │
│              │ 6.Generate   │───→ SSE 流式返回前端                      │
│              │   Response   │                                           │
│              └──────────────┘                                           │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
                                 │
                    ┌────────────┼────────────┐
                    ▼            ▼            ▼
┌──────────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│   PostgreSQL  │ │ pgvector │ │   GIN    │ │  B-tree  │
│   (主数据库)   │ │(HNSW索引)│ │(全文索引)│ │(结构化)  │
└──────────────┘ └──────────┘ └──────────┘ └──────────┘
                                 │
                    ┌────────────┼────────────┐
                    ▼            ▼            ▼
┌──────────────┐ ┌──────────┐ ┌──────────┐
│   向量检索     │ │ 全文检索  │ │ SQL过滤   │
│ (语义相似度)   │ │(关键词)  │ │ (结构化)  │
└──────────────┘ └──────────┘ └──────────┘
                                 │
                    ┌────────────┼────────────┐
                    ▼            ▼            ▼
┌──────────────┐ ┌──────────┐ ┌──────────┐
│    Redis      │ │  用户画像 │ │  Embedding│
│   (缓存层)    │ │  行为数据 │ │   服务    │
└──────────────┘ └──────────┘ └──────────┘
```

---

## 三、技术栈选型

### 3.1 分层技术选型

| 层级 | 选型 | 版本 | 选型理由 |
|------|------|------|---------|
| **前端框架** | React | 18+ | 并发渲染优化高频输入响应 |
| **前端语言** | TypeScript | 5.5+ | 编译时类型安全 |
| **UI样式** | Tailwind CSS | 3.4+ | Utility-first 快速构建 |
| **UI组件** | Shadcn/ui + Headless UI | latest | 可定制、可访问性支持 |
| **后端框架** | FastAPI | 0.115+ | 异步性能、自动API文档 |
| **Agent编排** | LangGraph | 0.2+ | 状态机工作流、条件路由 |
| **LLM SDK** | LangChain | 0.3+ | 工具链生态、pgvector集成 |
| **数据库** | PostgreSQL | 16+ | 关系+向量一体化 |
| **向量扩展** | pgvector | 0.7+ | HNSW/IVFFlat索引 |
| **缓存** | Redis | 7+ | 多级缓存、会话状态 |
| **Embedding** | OpenAI API | text-embedding-3-small | MVP快速验证（$0.02/百万token）|
| **LLM** | OpenAI API | GPT-4o-mini | 性价比最优（$0.15/百万token）|
| **部署** | Docker Compose | - | 开发一致性、一键启动 |

### 3.2 关键库依赖

```python
# Python 后端
fastapi==0.115.0
uvicorn[standard]==0.32.0
langgraph==0.2.0
langchain==0.3.0
langchain-openai==0.2.0
langchain-postgres==0.0.12
pgvector==0.3.0
asyncpg==0.30.0
sqlalchemy[asyncio]==2.0.35
redis==5.2.0
pydantic==2.9.0
pydantic-settings==2.6.0
python-dotenv==1.0.0

# TypeScript 前端
react==18.3.0
react-dom==18.3.0
typescript==5.6.0
tailwindcss==3.4.0
@radix-ui/react-*        # Headless UI 组件
class-variance-authority  # 组件变体管理
lucide-react             # 图标库
```

---

## 四、数据模型设计

### 4.1 核心表结构

```sql
-- 1. 商品主表（假设你已有类似结构，此为例示）
CREATE TABLE products (
    id              BIGSERIAL PRIMARY KEY,
    title           VARCHAR(200) NOT NULL,        -- 商品标题（短字段）
    category        VARCHAR(100),                 -- 类别
    brand           VARCHAR(100),                 -- 品牌
    price           DECIMAL(12,2),                -- 价格
    description     TEXT,                         -- 商品描述（长字段）
    specifications  JSONB,                        -- 规格参数（半结构化）
    tags            VARCHAR(50)[],                -- 标签数组
    rating          DECIMAL(2,1) DEFAULT 0,       -- 评分
    sales_count     INTEGER DEFAULT 0,            -- 销量
    status          VARCHAR(20) DEFAULT 'active', -- 状态
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- 2. 向量嵌入表（分离存储，支持多种嵌入策略）
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE product_embeddings (
    id              BIGSERIAL PRIMARY KEY,
    product_id      BIGINT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    embed_type      VARCHAR(20) NOT NULL DEFAULT 'combined', -- 'title' | 'description' | 'combined'
    embedding       VECTOR(1536),             -- OpenAI text-embedding-3-small 维度
    model_version   VARCHAR(50),              -- 嵌入模型版本
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(product_id, embed_type)
);

-- 3. 用户表
CREATE TABLE users (
    id              BIGSERIAL PRIMARY KEY,
    username        VARCHAR(100),
    email           VARCHAR(200),
    profile         JSONB,                    -- 用户画像数据
    preferences     JSONB,                    -- 偏好设置
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- 4. 用户行为表（用于个性化排序）
CREATE TABLE user_behaviors (
    id              BIGSERIAL PRIMARY KEY,
    user_id         BIGINT NOT NULL REFERENCES users(id),
    product_id      BIGINT NOT NULL REFERENCES products(id),
    action_type     VARCHAR(20) NOT NULL,     -- 'view' | 'click' | 'cart' | 'favorite' | 'purchase'
    action_value    DECIMAL(10,2) DEFAULT 0,  -- 购买金额等
    context         JSONB,                    -- 上下文（搜索关键词、设备等）
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- 5. 搜索日志表（用于分析和优化）
CREATE TABLE search_logs (
    id              BIGSERIAL PRIMARY KEY,
    user_id         BIGINT REFERENCES users(id),
    raw_query       TEXT NOT NULL,            -- 原始查询
    processed_query TEXT,                     -- 处理后查询
    intent_type     VARCHAR(50),              -- 识别的意图类型
    results_count   INTEGER,                  -- 返回结果数
    latency_ms      INTEGER,                  -- 响应延迟
    click_product_id BIGINT,                  -- 用户点击的商品
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
```

### 4.2 索引设计

```sql
-- HNSW 向量索引（高性能近似最近邻搜索）
CREATE INDEX idx_product_embeddings_hnsw
ON product_embeddings
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- GIN 全文搜索索引
CREATE INDEX idx_products_fts
ON products
USING GIN (to_tsvector('chinese', COALESCE(title,'') || ' ' || COALESCE(description,'')));

-- 结构化字段 B-tree 索引（用于SQL过滤）
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_brand ON products(brand);
CREATE INDEX idx_products_price ON products(price);
CREATE INDEX idx_products_status ON products(status);
CREATE INDEX idx_products_rating ON products(rating DESC);
CREATE INDEX idx_products_sales ON products(sales_count DESC);

-- JSONB 索引
CREATE INDEX idx_products_specifications ON products USING GIN (specifications);

-- 用户行为索引
CREATE INDEX idx_behaviors_user ON user_behaviors(user_id, created_at DESC);
CREATE INDEX idx_behaviors_product ON user_behaviors(product_id);
CREATE INDEX idx_behaviors_action ON user_behaviors(user_id, action_type, created_at DESC);
```

---

## 五、Agent 决策流程（核心）

### 5.1 流程图

```
用户输入: "我想买一件200元以内的蓝色运动T恤，要耐穿的"
    │
    ▼
┌───────────────────────────────────────────────────────┐
│ Step 1: Query Analysis (查询分析)                      │
│ • 语言检测: 中文                                        │
│ • 分词处理: "200元以内" / "蓝色" / "运动T恤" / "耐穿"    │
│ • 实体提取: price<200, color=blue, category=T恤        │
│ • 查询类型: 条件筛选型 (filtered_search)                │
└───────────────────────┬───────────────────────────────┘
                        │
┌───────────────────────▼───────────────────────────────┐
│ Step 2: Intent Classification (意图分类)               │
│ • 意图: purchase_intent (购买意图)                      │
│ • 紧急度: normal                                       │
│ • 价格敏感度: high (明确指定价格上限)                    │
│ • 品质偏好: high (提到"耐穿")                          │
└───────────────────────┬───────────────────────────────┘
                        │
┌───────────────────────▼───────────────────────────────┐
│ Step 3: Route Selection (路由决策)                     │
│ • 主策略: hybrid_search (混合检索)                      │
│ • 子策略:                                              │
│   - SQL预过滤: price <= 200 AND status = 'active'      │
│   - 向量检索: "蓝色运动T恤 耐穿" (语义)                  │
│   - 全文检索: "运动T恤" OR "蓝色T恤" (关键词)            │
│ • 融合方式: RRF (k=60)                                 │
└───────────────────────┬───────────────────────────────┘
                        │
┌───────────────────────▼───────────────────────────────┐
│ Step 4: Parallel Search (并行搜索)                     │
│ ┌───────────────┐  ┌───────────────┐  ┌─────────────┐ │
│ │ SQL过滤查询    │  │ 向量相似度搜索 │  │ 全文搜索    │ │
│ │ (B-tree索引)  │  │ (HNSW索引)    │  │ (GIN索引)  │ │
│ │ 返回: 候选集A  │  │ 返回: 候选集B  │  │ 返回: 候选集C│ │
│ └───────┬───────┘  └───────┬───────┘  └─────┬───────┘ │
│         └───────────────────┼─────────────────┘         │
│                             ▼                           │
│                     RRF 融合排序                         │
│                     返回: Top 50 候选                    │
└───────────────────────┬───────────────────────────────┘
                        │
┌───────────────────────▼───────────────────────────────┐
│ Step 5: Personalization Rerank (个性化重排序)          │
│ • 获取用户画像 & 历史行为                               │
│ • 个性化评分公式:                                       │
│   final_score = α×rrf_score                             │
│               + β×user_preference_match                 │
│               + γ×behavior_boost (点击×1.5 购买×10)     │
│ • 重新排序 Top 50 → Top 20                             │
└───────────────────────┬───────────────────────────────┘
                        │
┌───────────────────────▼───────────────────────────────┐
│ Step 6: Response Generation (响应生成)                 │
│ • 组装搜索结果列表                                       │
│ • 高亮匹配字段                                          │
│ • 生成 AI 推荐语: "根据您的需求，为您推荐以下耐穿的      │
│   蓝色运动T恤，均在200元以内..."                        │
│ • SSE 流式返回前端                                      │
└───────────────────────────────────────────────────────┘
```

### 5.2 LangGraph 状态定义

```python
from typing import TypedDict, List, Optional, Dict, Any
from langgraph.graph import StateGraph

class SearchState(TypedDict):
    # 输入
    query: str                          # 用户原始查询
    user_id: Optional[int]             # 用户ID（用于个性化）
    
    # Step 1-2: 分析结果
    analyzed_query: Optional[str]      # 解析后的查询
    entities: Optional[Dict[str, Any]] # 提取的实体
    intent: Optional[str]              # 意图类型
    
    # Step 3: 路由决策
    search_strategy: Optional[str]     # 搜索策略
    sql_filters: Optional[Dict]        # SQL过滤条件
    vector_query: Optional[str]        # 向量搜索文本
    
    # Step 4: 搜索结果
    candidates: Optional[List[Dict]]   # 候选结果
    
    # Step 5: 个性化
    reranked_results: Optional[List[Dict]]  # 重排序结果
    
    # Step 6: 输出
    response: Optional[Dict]           # 最终响应
    error: Optional[str]               # 错误信息
```

---

## 六、API 接口设计

### 6.1 核心端点

```yaml
# 主搜索接口（流式响应）
POST /api/v1/search
  Request:
    {
      "query": "蓝色运动T恤 200元以内",
      "user_id": 123,                    # optional
      "filters": {                       # optional
        "category": "服装",
        "price_max": 200
      },
      "sort_by": "relevance",            # relevance | price_asc | price_desc | sales | rating
      "page": 1,
      "page_size": 20
    }
  
  Response (SSE 流式):
    event: thinking
    data: {"step": "query_analysis", "content": "正在分析您的搜索意图..."}
    
    event: searching
    data: {"step": "vector_search", "content": "正在搜索相似商品..."}
    
    event: result
    data: {
      "products": [...],
      "total": 156,
      "ai_summary": "为您找到 156 件符合要求的商品，以下是最佳推荐...",
      "suggested_filters": [...]
    }

# 自动补全接口
GET /api/v1/suggest?q={query}&limit=8
  Response:
    {
      "suggestions": [
        {"type": "product", "text": "蓝色运动T恤", "product_id": 1001},
        {"type": "category", "text": "运动T恤", "category": "sportswear"},
        {"type": "brand", "text": "Nike 运动系列", "brand": "Nike"}
      ]
    }

# 筛选器选项接口
GET /api/v1/filters?category={category}
  Response:
    {
      "filters": [
        {"name": "brand", "type": "multi_select", "options": [...]},
        {"name": "price", "type": "range", "min": 0, "max": 1000},
        {"name": "rating", "type": "rating", "options": [4, 3, 2]}
      ]
    }

# 数据同步接口（用于更新embedding）
POST /api/v1/sync/products
  {
    "product_ids": [1, 2, 3],  # optional, 不传则全量同步
    "batch_size": 100
  }
```

---

## 七、MVP 功能范围

### 7.1 MVP 必须实现（P0）

| 模块 | 功能 | 说明 |
|------|------|------|
| 🔍 搜索框 | 自然语言搜索 | 用户输入任意文本，AI理解意图 |
| 🔍 搜索框 | 自动补全 | 输入时实时提示（基于标题前缀匹配）|
| 🧠 Agent | 意图识别 | LLM分类查询意图 |
| 🧠 Agent | 实体提取 | 提取品牌、类别、价格范围等 |
| 🔀 检索 | 向量搜索 | pgvector HNSW语义相似度 |
| 🔀 检索 | 全文搜索 | PostgreSQL GIN全文索引 |
| 🔀 检索 | SQL过滤 | 结构化条件预过滤 |
| 🔀 检索 | RRF融合 | 多路召回结果融合 |
| 📊 结果 | 列表展示 | 卡片式结果列表（图片、标题、价格、评分）|
| 📊 结果 | AI推荐语 | 搜索结果顶部的AI总结 |
| 🏗️ 基础 | Docker部署 | docker-compose一键启动 |

### 7.2 MVP 后续迭代（P1-P2）

| 优先级 | 功能 | 说明 |
|--------|------|------|
| P1 | 👤 用户画像 | 基础用户画像建模 |
| P1 | 👤 行为追踪 | 点击/收藏行为采集 |
| P1 | 📈 个性化排序 | 基于行为的简单加权排序 |
| P1 | 🔍 高级筛选器 | 多维度筛选UI |
| P2 | 💬 多轮对话 | 搜索上下文保持 |
| P2 | 🔄 查询重写 | 自动扩展/纠错 |
| P2 | 📊 搜索分析 | 日志分析和仪表盘 |
| P2 | 🧪 A/B测试 | 排序策略对比 |

---

## 八、部署架构

### 8.1 Docker Compose 配置

```yaml
# docker-compose.yml
version: '3.8'

services:
  # 前端
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - VITE_API_URL=http://localhost:8000
    depends_on:
      - backend

  # 后端 API
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/search_db
      - REDIS_URL=redis://redis:6379/0
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - EMBEDDING_MODEL=text-embedding-3-small
      - LLM_MODEL=gpt-4o-mini
    depends_on:
      - db
      - redis

  # PostgreSQL + pgvector
  db:
    image: ankane/pgvector:latest
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=search_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init:/docker-entrypoint-initdb.d

  # Redis 缓存
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

---

## 九、成本估算

### 9.1 MVP 月度成本（10万搜索请求/月）

| 项目 | 用量 | 单价 | 月费用 |
|------|------|------|--------|
| **Embedding API** | 100万 tokens | $0.02/百万 | ~$0.02 |
| **LLM API** | 500万 input + 100万 output tokens | $0.15/$0.60/百万 | ~$1.35 |
| **服务器** | 1台 4核8G (开发/测试) | ¥200/月 | ~$30 |
| **总计** | | | **~$32/月** |

### 9.2 生产预估（100万搜索/月）

| 项目 | 用量 | 单价 | 月费用 |
|------|------|------|--------|
| **Embedding API** | 1000万 tokens | $0.02/百万 | ~$0.20 |
| **LLM API** | 5000万 input + 1000万 output tokens | $0.15/$0.60/百万 | ~$13.50 |
| **服务器** | 2台 8核16G + 负载均衡 | ¥800/月 | ~$120 |
| **Redis** | 1台 4核8G | ¥200/月 | ~$30 |
| **总计** | | | **~$164/月** |

> 注：Embedding 成本初期很低（预计算存储），主要成本在 LLM 调用。后续切换 BGE-M3 自托管可大幅降低 Embedding 成本。

---

## 十、实施计划

### Phase 1: 基础设施（第1-2天）
- [ ] Docker Compose 环境搭建
- [ ] PostgreSQL + pgvector 配置
- [ ] Redis 配置
- [ ] 数据表和索引创建

### Phase 2: 数据层（第3-4天）
- [ ] 现有数据导入/对接
- [ ] Embedding 生成和存储（批处理百万数据）
- [ ] HNSW 索引构建

### Phase 3: AI Agent 核心（第5-8天）
- [ ] LangGraph 工作流搭建
- [ ] Query Analysis 节点
- [ ] Intent Classification 节点
- [ ] Route Selection 节点
- [ ] Parallel Search 节点
- [ ] RRF Fusion 节点
- [ ] Response Generation 节点

### Phase 4: API 层（第7-9天）
- [ ] FastAPI 项目结构
- [ ] /search 接口（SSE 流式）
- [ ] /suggest 接口
- [ ] /sync 接口
- [ ] 错误处理和降级

### Phase 5: 前端（第8-11天）
- [ ] 搜索框组件 + 自动补全
- [ ] 结果列表 + 筛选器
- [ ] SSE 流式响应处理
- [ ] 响应式适配

### Phase 6: 集成测试（第11-12天）
- [ ] 端到端测试
- [ ] 性能测试
- [ ] Bug修复和优化

**预估总工期: 10-12个工作日**

---

## 十一、风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| HNSW索引构建时间长 | 高 | 后台异步构建，分批次处理 |
| LLM调用延迟(2-5s) | 中 | SSE流式响应 + Agent步骤提示 |
| Embedding API限流 | 中 | 批处理 + 指数退避重试 |
| 个性化冷启动 | 中 | 默认排序 + 实时信号采集 |
| 查询理解不准确 | 低 | 规则兜底 + 多轮反馈优化 |

---

*本方案基于 10 维度深度研究（160+ 次搜索、50+ 权威来源）和交叉验证，等待确认后进入 MVP 开发阶段。*
