# AI 智能搜索插件 — MVP 完整方案

> 版本: v2.0 (通用化架构) | 日期: 2026-06-09
> 基于 15 维度深度研究（220+ 次搜索、150+ 权威来源）+ 交叉验证

---

## 目录

1. [项目概述](#一项目概述)
2. [核心设计理念](#二核心设计理念)
3. [系统架构](#三系统架构)
4. [通用配置层设计](#四通用配置层设计核心)
5. [数据模型设计](#五数据模型设计)
6. [Agent 决策流程](#六agent-决策流程)
7. [API 接口设计](#七api-接口设计)
8. [前端组件设计](#八前端组件设计)
9. [部署架构](#九部署架构)
10. [实施计划](#十实施计划)
11. [成本估算](#十一成本估算)
12. [使用指南](#十二使用指南)
13. [边界与限制](#十三边界与限制)

---

## 一、项目概述

### 1.1 项目目标

构建一个**通用 AI 搜索插件**，核心能力：

| 特性 | 说明 |
|------|------|
| 🔌 **通用接入** | 任意 PostgreSQL 数据表，通过 YAML 配置即可接入 |
| ⚡ **极简配置** | 30 秒上手：只填表名，系统自动发现所有配置 |
| 🔧 **基础可调** | 5 分钟：微调字段权重、搜索策略、UI 展示 |
| 🎛️ **高级可选** | 30 分钟（可选）：自定义模板、插件、同义词 |
| 🧠 **Agent 驱动** | LangGraph Agent 理解意图，动态选择检索策略 |
| 🔀 **混合检索** | 向量语义搜索 + 全文关键词搜索 + SQL 结构化过滤 |
| 👤 **个性化** | 融合用户画像、历史行为、内容动态排序 |
| 📊 **百万数据** | 基于现有 PostgreSQL，无需数据迁移 |

### 1.2 一句话定位

> "像 Algolia 一样简单配置，像 ChatGPT 一样智能搜索"

### 1.3 技术栈

| 层级 | 选型 | 版本 |
|------|------|------|
| 前端框架 | React | 18+ |
| 前端语言 | TypeScript | 5.5+ |
| UI 样式 | Tailwind CSS | 3.4+ |
| UI 组件 | Shadcn/ui + Headless UI | latest |
| 后端框架 | FastAPI | 0.115+ |
| Agent 编排 | LangGraph | 0.2+ |
| LLM SDK | LangChain | 0.3+ |
| 数据库 | PostgreSQL | 16+ |
| 向量扩展 | pgvector | 0.7+ |
| 缓存 | Redis | 7+ |
| Embedding | OpenAI API | text-embedding-3-small |
| LLM | OpenAI API | GPT-4o-mini |
| 部署 | Docker Compose | - |

---

## 二、核心设计理念

### 2.1 五层配置模型

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 5: 行为配置 (Behavior)                                │
│  - 防抖时间、分页大小、高亮、排序默认                          │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│  Layer 4: 展示模板 (Presentation)                            │
│  - 卡片布局、字段展示顺序、筛选器面板、排序选项                   │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│  Layer 3: 检索策略 (Retrieval)                               │
│  - 向量/全文/SQL权重、RRF参数、同义词、停用词                  │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│  Layer 2: 字段映射 (Field Mapping)                           │
│  - 哪些字段参与搜索、Embedding策略、权重、过滤/排序/面过滤       │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: 数据源 (Data Source)                               │
│  - PostgreSQL连接、表名、主键、Schema发现配置                   │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 渐进式配置策略

| 配置级别 | 所需时间 | 覆盖场景 | 用户操作 | 技术要求 |
|----------|---------|---------|---------|---------|
| **极简模式** | 30 秒 | ~60% | 只填表名 | 任何开发者 |
| **基础配置** | 5 分钟 | ~25% | 微调字段权重和搜索策略 | 理解基本配置 |
| **高级配置** | 30 分钟 | ~12% | 自定义模板、插件、同义词 | 深入理解搜索原理 |
| **定制开发** | 2 天+ | ~3% | 编写自定义插件 | 搜索工程经验 |

### 2.3 极简接入示例

```python
# Python SDK 风格 — 30秒接入
from ai_search import SearchEngine

engine = SearchEngine.from_yaml("config.yaml")
engine.serve(port=8000)
```

```yaml
# config.yaml — 极简配置（只有表名是必需的）
data_source:
  table: products
  # 其他全部自动生成！
```

系统自动完成：
1. ✅ 扫描表结构（`information_schema.columns`）
2. ✅ 推断字段类型和权重（`title`→高权重, `price`→过滤条件）
3. ✅ 生成 Embedding 策略（组合文本字段）
4. ✅ 创建 HNSW + GIN 索引
5. ✅ 启动搜索 API + UI

---

## 三、系统架构

### 3.1 整体架构图

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         前端层 (React + TypeScript)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  搜索框组件   │  │  自动补全    │  │  筛选器面板   │  │  结果列表     │ │
│  │  (SearchBox) │  │  (Suggest)   │  │  (Filters)   │  │  (Results)   │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘ │
│         └─────────────────┴─────────────────┴─────────────────┘         │
│                                    │ SSE 流式                            │
└────────────────────────────────────┼─────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼─────────────────────────────────────┐
│                      API 网关层 (FastAPI async)                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  POST /search │  │  GET /suggest│  │ GET /filters │  │ POST /sync   │ │
│  │  SSE 流式     │  │  自动补全    │  │  筛选器选项  │  │ 同步索引     │ │
│  └──────┬───────┘  └──────────────┘  └──────────────┘  └──────────────┘ │
│         │                                                               │
└─────────┼───────────────────────────────────────────────────────────────┘
          │
┌─────────▼───────────────────────────────────────────────────────────────┐
│              通用化配置层 (Configuration Layer) — MVP 核心新增              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐      │
│  │  Schema 发现服务  │  │  配置管理模块     │  │  字段分类引擎     │      │
│  │  SchemaDiscovery │  │  ConfigManager   │  │  FieldClassifier │      │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘      │
│           │                     │                     │                 │
│           └─────────────────────┼─────────────────────┘                 │
│                                 ▼                                       │
│                    ┌────────────────────────┐                           │
│                    │   动态 Embedding 生成   │                           │
│                    │   DynamicEmbedding     │                           │
│                    └────────────────────────┘                           │
└─────────────────────────────────────────────────────────────────────────┘
          │
┌─────────▼───────────────────────────────────────────────────────────────┐
│              AI Agent 编排层 (LangGraph StateGraph)                        │
│                                                                          │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐        │
│   │ 1.Query  │───→│ 2.Intent │───→│ 3.Route  │───→│ 4.Search │        │
│   │ Analysis │    │ Classify │    │ Select   │    │ Execute  │        │
│   └──────────┘    └──────────┘    └──────────┘    └────┬─────┘        │
│         ▲                                              │                │
│         │           ┌──────────┐    ┌──────────┐       │                │
│         └───────────│ 7.Feedback│←───│ 5.Rerank │←──────┘                │
│                     │  Loop    │    │ & Format │                        │
│                     └──────────┘    └────┬─────┘                        │
│                                          │                               │
│                     ┌────────────────────┘                               │
│                     ▼                                                    │
│              ┌──────────────┐                                           │
│              │ 6.Generate   │───→ SSE 流式返回前端                      │
│              │   Response   │                                           │
│              └──────────────┘                                           │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
          │
          ├──────────────────────────────────────────────────────────────┐
          │                              │                               │
┌─────────▼──────────┐  ┌───────────────▼────────┐  ┌───────────────────▼─┐
│   PostgreSQL       │  │   PostgreSQL           │  │   PostgreSQL        │
│   pgvector         │  │   GIN                  │  │   B-tree            │
│   (HNSW索引)       │  │   (全文索引)            │  │   (结构化)           │
│   向量检索         │  │   全文检索              │  │   SQL过滤            │
└────────────────────┘  └────────────────────────┘  └─────────────────────┘
          │
┌─────────▼──────────┐  ┌────────────────────────┐
│     Redis          │  │   OpenAI API           │
│   查询缓存         │  │   Embedding + LLM      │
│   会话状态         │  │   (GPT-4o-mini)        │
└────────────────────┘  └────────────────────────┘
```

### 3.2 关键设计决策

| 决策项 | 选择 | 理由 |
|--------|------|------|
| Agent 编排 | LangGraph StateGraph | 状态机工作流、条件路由、持久化 |
| Embedding | OpenAI API (MVP) | $0.02/百万token，快速验证 |
| LLM | GPT-4o-mini | $0.15/百万token，工具调用能力足够 |
| 索引 | HNSW (m=16, ef=64) | 查询快15倍 vs IVFFlat，召回率~95% |
| 融合 | RRF (k=60) | 跨域鲁棒，业界标准 |
| 个性化 | MVP 阶段规则权重 | 行为权重：购买×10 > 加购×6 > 收藏×4 > 点击×1.5 |

---

## 四、通用配置层设计（核心）

### 4.1 配置 Schema 定义

```yaml
# ============================================================
# AI Search Plugin — 通用配置 Schema
# ============================================================
# 配置级别说明:
#   [必填]   — 极简模式也需要
#   [推荐]   — 基础配置建议填写
#   [可选]   — 高级配置可选
#   [自动生成] — 系统根据 Schema 自动推断，可覆盖
# ============================================================

# Layer 1: 数据源配置
# 极简模式: 只需 table
# 基础模式: 添加 pool_size, timeout
data_source:
  table: products                    # [必填] 主表名
  primary_key: id                   # [自动生成] 主键字段
  connection_pool:                  # [可选] 连接池配置
    min_size: 5
    max_size: 20
    timeout: 30
  schema_discovery:                 # [可选] Schema 发现配置
    sample_size: 100                # 采样行数
    ignore_patterns: ["id", "created_at", "updated_at"]  # 忽略字段模式
    custom_type_rules: []           # 自定义类型规则

# Layer 2: 字段映射配置
# 极简模式: 全部自动生成
# 基础模式: 微调 weight, searchable, filterable
fields:
  # 字段配置格式:
  # <字段名>:
  #   type: short_text | long_text | category | number | boolean | json | date | image_url | ignore
  #   display_name: "中文展示名"                        # [自动生成]
  #   searchable: true | false                         # [自动生成]
  #   filterable: true | false                         # [自动生成]
  #   sortable: true | false                           # [自动生成]
  #   facetable: true | false                          # [自动生成]
  #   weight: 0.0 ~ 1.0                                # [自动生成]
  #   embedding_strategy: combined | separate | ignore # [自动生成]
  #   formatter: currency | percentage | date | compact_number  # [可选]
  #   max_length: 100                                   # [可选] 展示最大长度

  # 示例: 自动生成的字段配置
  title:
    type: short_text
    display_name: "商品标题"
    searchable: true
    filterable: false
    sortable: false
    facetable: false
    weight: 1.0
    embedding_strategy: combined

  description:
    type: long_text
    display_name: "商品描述"
    searchable: true
    filterable: false
    sortable: false
    facetable: false
    weight: 0.6
    embedding_strategy: separate

  price:
    type: number
    display_name: "价格"
    searchable: false
    filterable: true
    sortable: true
    facetable: false
    weight: 0.0
    formatter: currency

  category:
    type: category
    display_name: "类别"
    searchable: true
    filterable: true
    sortable: false
    facetable: true
    weight: 0.5
    embedding_strategy: combined

  brand:
    type: category
    display_name: "品牌"
    searchable: true
    filterable: true
    sortable: false
    facetable: true
    weight: 0.8
    embedding_strategy: combined

  rating:
    type: number
    display_name: "评分"
    searchable: false
    filterable: true
    sortable: true
    facetable: true
    weight: 0.0

  image_url:
    type: image_url
    display_name: "商品图片"
    searchable: false
    filterable: false
    sortable: false
    facetable: false
    weight: 0.0

  created_at:
    type: date
    display_name: "上架时间"
    searchable: false
    filterable: true
    sortable: true
    facetable: false
    weight: 0.0

  status:
    type: ignore                           # 不索引此字段
    display_name: "状态"

# Layer 3: 检索策略配置
# 极简模式: 全部自动选择
# 基础模式: 调整权重和参数
search:
  strategies:                           # 启用哪些检索策略
    vector: true                        # 向量语义搜索
    fulltext: true                      # PostgreSQL 全文搜索
    sql_filter: true                    # SQL 结构化过滤
  weights:                              # 各策略结果融合权重
    vector: 0.5
    fulltext: 0.3
    sql_filter: 0.2
  rrf:                                  # RRF 融合参数
    k: 60
  embedding:                            # Embedding 配置
    model: openai:text-embedding-3-small  # [自动生成]
    dimensions: 1536                    # [自动生成]
    batch_size: 100
    template: ecommerce                 # Embedding 模板名
  fulltext:                             # 全文搜索配置
    language: chinese                    # 分词语言
    highlight: true                      # 高亮匹配
  synonyms: []                          # [可选] 同义词词典
  stopwords: []                         # [可选] 停用词列表

# Layer 4: 展示模板配置
# 极简模式: 使用默认卡片模板
# 基础模式: 调整字段展示顺序
presentation:
  result_template: card                 # card | list | compact
  fields_order:                         # 字段展示优先级
    - image_url
    - title
    - price
    - rating
    - brand
    - category
  card_layout:                          # 卡片布局配置
    image_position: top                 # top | left
    show_labels: false                  # 是否显示字段标签
    max_title_length: 50
    badges: [brand, category]           # 作为 badge 展示的字段
  highlight:                            # 匹配高亮配置
    enabled: true
    prefix: "<mark>"
    suffix: "</mark>"
  empty_state:                          # 无结果展示
    title: "未找到相关商品"
    subtitle: "试试其他关键词，或调整筛选条件"
    suggestions: true                   # 是否展示推荐

# Layer 5: 行为配置
# 极简模式: 使用默认值
behavior:
  debounce_ms: 300                      # 输入防抖（毫秒）
  suggest_delay_ms: 100                 # 自动补全延迟
  page_size: 20                         # 每页结果数
  max_page_size: 100                    # 最大每页数
  min_query_length: 1                   # 最小查询长度
  default_sort: relevance               # relevance | price_asc | price_desc | rating | sales
  sort_options:                         # 可用排序选项
    - { value: "relevance", label: "相关性" }
    - { value: "price_asc", label: "价格从低到高" }
    - { value: "price_desc", label: "价格从高到低" }
    - { value: "rating", label: "评分最高" }
    - { value: "sales", label: "销量最高" }
    - { value: "newest", label: "最新上架" }
  cache:                                # 缓存配置
    query_ttl_seconds: 300              # 查询结果缓存 5 分钟
    suggest_ttl_seconds: 60             # 补全建议缓存 1 分钟
  personalization:                      # 个性化配置（MVP 阶段简化）
    enabled: true
    cold_start_strategy: popular        # 冷启动策略: popular | newest | random
    behavior_weights:                   # 行为权重
      view: 1
      click: 3
      cart: 6
      favorite: 8
      purchase: 15
```

### 4.2 Schema 自动发现机制

```python
# 系统自动执行的发现流程
class SchemaDiscovery:
    async def discover(self, conn, table_name: str) -> TableSchema:
        # Step 1: 查询表结构
        columns = await conn.fetch("""
            SELECT column_name, data_type, character_maximum_length,
                   is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = $1 AND table_schema = 'public'
            ORDER BY ordinal_position
        """, table_name)

        # Step 2: 采样数据分析
        sample = await conn.fetch(f'SELECT * FROM "{table_name}" LIMIT 100')

        # Step 3: 智能字段分类
        fields = {}
        for col in columns:
            field = self.classify_field(col, sample)
            fields[col['column_name']] = field

        # Step 4: 识别主键
        pk = await self.find_primary_key(conn, table_name)

        # Step 5: 生成完整配置
        return self.generate_config(fields, pk)

    def classify_field(self, col, sample) -> FieldConfig:
        name = col['column_name'].lower()
        dtype = col['data_type'].lower()

        # 规则1: 系统字段 → ignore
        if name in ['id', 'created_at', 'updated_at', 'deleted_at']:
            return FieldConfig(type='ignore', weight=0)

        # 规则2: 图像URL字段
        if any(kw in name for kw in ['image', 'img', 'photo', 'picture', 'cover', 'thumbnail']):
            return FieldConfig(type='image_url', weight=0)

        # 规则3: 标题/名称字段 → short_text, weight=1.0
        if any(kw in name for kw in ['title', 'name', 'subject', 'headline']):
            return FieldConfig(type='short_text', weight=1.0, searchable=True)

        # 规则4: 描述/内容字段 → long_text, weight=0.6
        if any(kw in name for kw in ['description', 'content', 'body', 'detail', 'summary']):
            return FieldConfig(type='long_text', weight=0.6, searchable=True)

        # 规则5: 类别/标签字段 → category, weight=0.5
        if any(kw in name for kw in ['category', 'tag', 'label', 'type', 'genre']):
            return FieldConfig(type='category', weight=0.5, searchable=True, filterable=True, facetable=True)

        # 规则6: 品牌字段 → category, weight=0.8
        if any(kw in name for kw in ['brand', 'manufacturer', 'maker']):
            return FieldConfig(type='category', weight=0.8, searchable=True, filterable=True, facetable=True)

        # 规则7: 价格字段 → number, formatter=currency
        if any(kw in name for kw in ['price', 'cost', 'amount', 'fee']):
            return FieldConfig(type='number', weight=0, filterable=True, sortable=True, formatter='currency')

        # 规则8: 评分字段 → number
        if any(kw in name for kw in ['rating', 'score', 'rate', 'star']):
            return FieldConfig(type='number', weight=0, filterable=True, sortable=True)

        # 规则9: 数量/销量字段 → number
        if any(kw in name for kw in ['count', 'quantity', 'stock', 'sales', 'sold']):
            return FieldConfig(type='number', weight=0, filterable=True, sortable=True)

        # 规则10: URL字段 → ignore (或 link)
        if any(kw in name for kw in ['url', 'link', 'href']):
            return FieldConfig(type='ignore', weight=0)

        # 规则11: 布尔字段 → category
        if dtype in ['boolean']:
            return FieldConfig(type='category', weight=0, filterable=True, facetable=True)

        # 规则12: JSON字段 → json
        if dtype in ['json', 'jsonb']:
            return FieldConfig(type='json', weight=0.3, searchable=True)

        # 规则13: 时间字段 → date
        if dtype in ['timestamp', 'timestamptz', 'date']:
            return FieldConfig(type='date', weight=0, filterable=True, sortable=True)

        # 规则14: 数值字段 → number
        if dtype in ['integer', 'bigint', 'numeric', 'decimal', 'real', 'double precision']:
            return FieldConfig(type='number', weight=0, filterable=True, sortable=True)

        # 规则15: 长文本 → long_text
        if dtype in ['text'] or (col['character_maximum_length'] and col['character_maximum_length'] > 500):
            return FieldConfig(type='long_text', weight=0.5, searchable=True)

        # 默认: 短文本 → short_text
        return FieldConfig(type='short_text', weight=0.7, searchable=True)
```

### 4.3 Embedding 模板系统

```yaml
# 预定义模板库
templates:
  ecommerce:
    formatting: "{title}。{category}品牌{brand}。{description}"
    chunking: false
    weights:
      title: 1.0
      brand: 0.8
      category: 0.6
      description: 0.5
      tags: 0.5

  article:
    formatting: "{title}\n{summary}\n{content}"
    chunking: true
    chunk_size: 512
    chunk_overlap: 50
    weights:
      title: 1.0
      summary: 0.7
      content: 0.5

  knowledge_base:
    formatting: "{title}\n{category}\n{content}"
    chunking: true
    chunk_size: 1000
    weights:
      title: 1.0
      category: 0.6
      content: 0.5

  user_profile:
    formatting: "{name}，{title}，{bio}，{skills}"
    chunking: false
    weights:
      name: 1.0
      title: 0.8
      bio: 0.6
      skills: 0.7

  default:
    formatting: "{field1}。{field2}。{field3}"
    chunking: auto
    weights:
      "*": 0.7    # 默认权重
```

---

## 五、数据模型设计

### 5.1 核心表结构

```sql
-- ============================================================
-- 用户数据表（示例：由用户提供，不需要创建）
-- ============================================================
-- CREATE TABLE products (
--     id              BIGSERIAL PRIMARY KEY,
--     title           VARCHAR(200) NOT NULL,
--     category        VARCHAR(100),
--     brand           VARCHAR(100),
--     price           DECIMAL(12,2),
--     description     TEXT,
--     specifications  JSONB,
--     rating          DECIMAL(2,1) DEFAULT 0,
--     sales_count     INTEGER DEFAULT 0,
--     image_url       VARCHAR(500),
--     status          VARCHAR(20) DEFAULT 'active',
--     created_at      TIMESTAMPTZ DEFAULT NOW(),
--     updated_at      TIMESTAMPTZ DEFAULT NOW()
-- );

-- ============================================================
-- 插件自动创建的表
-- ============================================================

-- 1. 向量嵌入表（与主表分离，支持多策略）
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE {table}_embeddings (
    id              BIGSERIAL PRIMARY KEY,
    {primary_key}   BIGINT NOT NULL REFERENCES {table}({primary_key}) ON DELETE CASCADE,
    embed_type      VARCHAR(20) NOT NULL DEFAULT 'combined',
    embedding       VECTOR(1536),
    model_version   VARCHAR(50),
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE({primary_key}, embed_type)
);

-- 2. HNSW 向量索引
CREATE INDEX idx_{table}_embeddings_hnsw
ON {table}_embeddings
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- 3. GIN 全文搜索索引（在复合文本列上）
CREATE INDEX idx_{table}_fts
ON {table}
USING GIN (
    to_tsvector('simple',
        COALESCE(title,'') || ' ' ||
        COALESCE(brand,'') || ' ' ||
        COALESCE(category,'') || ' ' ||
        COALESCE(description,'')
    )
);

-- 4. 用户行为表（用于个性化）
CREATE TABLE user_behaviors (
    id              BIGSERIAL PRIMARY KEY,
    user_id         BIGINT NOT NULL,
    item_id         BIGINT NOT NULL,
    action_type     VARCHAR(20) NOT NULL,
    action_value    DECIMAL(10,2) DEFAULT 0,
    context         JSONB,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- 5. 搜索日志表
CREATE TABLE search_logs (
    id              BIGSERIAL PRIMARY KEY,
    user_id         BIGINT,
    raw_query       TEXT NOT NULL,
    processed_query TEXT,
    intent_type     VARCHAR(50),
    results_count   INTEGER,
    latency_ms      INTEGER,
    click_item_id   BIGINT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- 6. 配置存储表
CREATE TABLE search_configs (
    id              BIGSERIAL PRIMARY KEY,
    table_name      VARCHAR(100) NOT NULL UNIQUE,
    config_json     JSONB NOT NULL,
    version         INTEGER DEFAULT 1,
    is_active       BOOLEAN DEFAULT true,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 六、Agent 决策流程

### 6.1 LangGraph 状态定义

```python
from typing import TypedDict, Optional, List, Dict, Any

class SearchState(TypedDict):
    # === 输入 ===
    query: str
    user_id: Optional[int]
    filters: Optional[Dict[str, Any]]
    sort_by: Optional[str]
    page: int
    page_size: int

    # === Step 1: Query Analysis ===
    analyzed_query: Optional[str]
    entities: Optional[Dict[str, Any]]  # {price_max: 200, color: "blue", category: "T恤"}

    # === Step 2: Intent Classification ===
    intent: Optional[str]  # "purchase" | "browse" | "compare" | "exact"
    price_sensitivity: Optional[str]  # "high" | "medium" | "low"
    quality_preference: Optional[str]  # "high" | "medium" | "low"

    # === Step 3: Route Selection ===
    search_strategy: Optional[str]  # "hybrid" | "vector_only" | "fulltext_only" | "sql_only"
    sql_filters: Optional[Dict]  # {price: {lte: 200}, status: "active"}
    vector_query: Optional[str]  # "蓝色运动T恤 耐穿"
    fulltext_query: Optional[str]  # "运动T恤 | 蓝色T恤"

    # === Step 4: Search Results ===
    vector_results: Optional[List[Dict]]
    fulltext_results: Optional[List[Dict]]
    sql_results: Optional[List[Dict]]
    candidates: Optional[List[Dict]]  # RRF融合后

    # === Step 5: Personalization ===
    reranked_results: Optional[List[Dict]]
    ai_summary: Optional[str]

    # === Step 6: Output ===
    response: Optional[Dict]
    error: Optional[str]
```

### 6.2 流程图

```
用户输入: "我想买一件200元以内的蓝色运动T恤，要耐穿的"
    │
    ▼
┌──────────────────────────────────────────────────────┐
│ Step 1: Query Analysis                               │
│ 功能: 实体提取、查询预处理、语言检测                    │
│ 输出: entities = {price_max: 200, color: "blue",      │
│                  category: "运动T恤", quality: "耐穿"} │
└───────────────────────┬──────────────────────────────┘
                        │
┌───────────────────────▼──────────────────────────────┐
│ Step 2: Intent Classification (LLM)                  │
│ 功能: 意图分类、价格敏感度、品质偏好                    │
│ 输出: intent = "purchase_intent",                     │
│       price_sensitivity = "high",                     │
│       quality_preference = "high"                     │
└───────────────────────┬──────────────────────────────┘
                        │
┌───────────────────────▼──────────────────────────────┐
│ Step 3: Route Selection                              │
│ 功能: 根据配置选择检索策略                            │
│ 输出: search_strategy = "hybrid",                     │
│       sql_filters = {price: {lte: 200}},              │
│       vector_query = "蓝色运动T恤 耐穿",               │
│       fulltext_query = "运动T恤 蓝色"                  │
└───────────────────────┬──────────────────────────────┘
                        │
┌───────────────────────▼──────────────────────────────┐
│ Step 4: Parallel Search (并行)                       │
│ ┌────────────────┐  ┌────────────────┐               │
│ │ SQL预过滤       │  │ 向量搜索        │  ┌──────────┐│
│ │ 价格≤200        │  │ 语义相似度      │  │ 全文搜索  ││
│ │ 状态=active     │  │ HNSW索引        │  │ GIN索引   ││
│ └───────┬────────┘  └───────┬────────┘  └─────┬────┘│
│         └───────────────────┼──────────────────┘      │
│                             ▼                          │
│                      RRF 融合排序                       │
│                      返回 Top 50                       │
└───────────────────────┬──────────────────────────────┘
                        │
┌───────────────────────▼──────────────────────────────┐
│ Step 5: Personalization Rerank                       │
│ 功能: 用户画像加权、行为加权                           │
│ 公式: final_score = α×rrf + β×pref_match + γ×behavior│
│ 输出: Top 20 个性化排序结果                            │
└───────────────────────┬──────────────────────────────┘
                        │
┌───────────────────────▼──────────────────────────────┐
│ Step 6: Response Generation (LLM)                    │
│ 功能: AI 推荐语生成、结果组装                          │
│ 输出: {products: [...], ai_summary: "...",           │
│       total: 156, filters: [...]}                     │
└───────────────────────┬──────────────────────────────┘
                        │
                        ▼
                  SSE 流式返回
```

---

## 七、API 接口设计

### 7.1 核心端点

```yaml
# 主搜索接口（SSE 流式）
POST /api/v1/search
  Content-Type: application/json
  Accept: text/event-stream

  Request:
    {
      "query": "蓝色运动T恤 200元以内",
      "user_id": 123,
      "filters": {
        "category": "服装",
        "price_max": 200,
        "brand": ["Nike", "Adidas"]
      },
      "sort_by": "relevance",
      "page": 1,
      "page_size": 20
    }

  Response (SSE):
    event: step
    data: {"step": "query_analysis", "message": "正在分析您的搜索意图..."}

    event: step
    data: {"step": "searching", "message": "正在搜索相似商品..."}

    event: result
    data: {
      "products": [
        {
          "id": 1001,
          "title": "Nike 蓝色速干运动T恤",
          "price": 189.00,
          "brand": "Nike",
          "category": "运动T恤",
          "rating": 4.8,
          "image_url": "https://...",
          "score": 0.92,
          "highlights": {"title": "<mark>蓝色</mark><mark>运动T恤</mark>"}
        }
      ],
      "total": 156,
      "page": 1,
      "page_size": 20,
      "ai_summary": "为您找到 156 件符合要求的商品，推荐 Nike 和 Adidas 品牌的速干系列...",
      "suggested_filters": [
        {"field": "brand", "options": ["Nike (45)", "Adidas (32)", "李宁 (28)"]},
        {"field": "price", "ranges": ["0-100 (12)", "100-200 (89)", "200+ (55)"]}
      ],
      "query_analysis": {
        "intent": "purchase",
        "entities": {"price_max": 200, "color": "blue", "category": "运动T恤"}
      }
    }

# 自动补全接口
GET /api/v1/suggest?q={query}&limit=8
  Response:
    {
      "suggestions": [
        {"type": "query", "text": "蓝色运动T恤", "highlight": "<mark>蓝色</mark>运动T恤"},
        {"type": "product", "text": "Nike 蓝色速干T恤", "product_id": 1001, "image": "..."},
        {"type": "category", "text": "运动T恤", "category": "sportswear"},
        {"type": "brand", "text": "Nike 运动系列", "brand": "Nike"}
      ]
    }

# 筛选器选项接口
GET /api/v1/filters?applied={filters_json}
  Response:
    {
      "filters": [
        {"name": "brand", "type": "multi_select", "label": "品牌",
         "options": [{"value": "Nike", "count": 45}, {"value": "Adidas", "count": 32}]},
        {"name": "price", "type": "range", "label": "价格",
         "min": 0, "max": 1000},
        {"name": "rating", "type": "rating", "label": "评分",
         "options": [{"value": 4, "label": "4星及以上"}]}
      ]
    }

# 配置获取接口
GET /api/v1/config
  Response:
    {
      "table": "products",
      "fields": [...],
      "search": {...},
      "presentation": {...}
    }

# 索引同步接口
POST /api/v1/sync
  {
    "item_ids": [1, 2, 3],
    "full_rebuild": false
  }
  Response:
    {
      "status": "started",
      "total_items": 1000000,
      "batch_size": 100,
      "estimated_seconds": 600
    }

# 健康检查
GET /api/v1/health
  Response:
    {
      "status": "ok",
      "database": "connected",
      "redis": "connected",
      "openai": "available",
      "indexed_items": 1000000
    }
```

---

## 八、前端组件设计

### 8.1 组件结构

```
frontend/
├── src/
│   ├── components/
│   │   ├── SearchBox/           # 搜索框 + 自动补全
│   │   ├── FilterPanel/         # 筛选器面板
│   │   ├── ResultList/          # 结果列表
│   │   ├── ResultCard/          # 结果卡片
│   │   ├── SortBar/             # 排序栏
│   │   ├── Pagination/          # 分页
│   │   ├── AISummary/           # AI 推荐语
│   │   ├── SuggestionDropdown/  # 自动补全下拉
│   │   └── EmptyState/          # 无结果状态
│   ├── hooks/
│   │   ├── useSearch.ts         # 搜索逻辑 + SSE
│   │   ├── useSuggest.ts        # 自动补全
│   │   ├── useFilters.ts        # 筛选器
│   │   └── useConfig.ts         # 配置获取
│   ├── types/
│   │   └── index.ts             # TypeScript 类型定义
│   ├── services/
│   │   └── api.ts               # API 调用层
│   └── App.tsx
```

### 8.2 核心组件设计

```typescript
// SearchBox 组件
interface SearchBoxProps {
  value: string;
  onChange: (value: string) => void;
  onSearch: (query: string) => void;
  suggestions: Suggestion[];
  loading: boolean;
  placeholder?: string;
  debounceMs?: number;
}

// ResultCard 组件（配置驱动）
interface ResultCardProps {
  item: Record<string, any>;        // 任意数据项
  config: PresentationConfig;       // 展示配置
  highlights?: Record<string, string>; // 高亮
}

// 配置驱动渲染
const ResultCard: React.FC<ResultCardProps> = ({ item, config, highlights }) => {
  const fields = config.fields_order
    .map(name => config.fields[name])
    .filter(Boolean);

  return (
    <div className={`result-card layout-${config.card_layout.image_position}`}>
      {fields.map(field => (
        <FieldRenderer
          key={field.name}
          value={item[field.name]}
          config={field}
          highlight={highlights?.[field.name]}
        />
      ))}
    </div>
  );
};
```

---

## 九、部署架构

### 9.1 Docker Compose

```yaml
version: '3.8'

services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - VITE_API_URL=http://localhost:8000

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/search_db
      - REDIS_URL=redis://redis:6379/0
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - db
      - redis

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

### 9.2 部署命令

```bash
# 1. 克隆项目
git clone <repo> ai-search-plugin
cd ai-search-plugin

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 填入 OPENAI_API_KEY

# 3. 启动服务
docker-compose up -d

# 4. 创建配置文件 config.yaml（极简: 只需表名）
echo "data_source:
  table: products" > config.yaml

# 5. 运行 Schema 发现 + 初始化
python -m ai_search init --config config.yaml

# 6. 启动搜索服务
docker-compose up -d

# 访问 http://localhost:3000 查看搜索界面
```

---

## 十、实施计划

### 10.1 Phase 1: 基础设施（第1-2天）

| 任务 | 工时 | 负责人 |
|------|------|--------|
| Docker Compose 环境搭建 | 4h | Dev |
| PostgreSQL + pgvector 配置 | 3h | Dev |
| Redis 配置 | 1h | Dev |
| 项目脚手架 + 依赖管理 | 2h | Dev |

### 10.2 Phase 2: 通用化配置层（第3-4天）⭐核心

| 任务 | 工时 | 负责人 |
|------|------|--------|
| Schema 发现服务（自动扫描表结构） | 6h | Dev |
| 字段分类引擎（15条规则） | 4h | Dev |
| 配置管理模块（加载/验证/存储） | 4h | Dev |
| 配置 Schema 验证（Pydantic） | 2h | Dev |
| 默认配置生成器 | 2h | Dev |

### 10.3 Phase 3: AI Agent 核心（第5-8天）

| 任务 | 工时 | 负责人 |
|------|------|--------|
| LangGraph 工作流搭建 | 4h | Dev |
| Query Analysis 节点（实体提取） | 6h | Dev |
| Intent Classification 节点 | 4h | Dev |
| Route Selection 节点 | 4h | Dev |
| Parallel Search 节点 | 8h | Dev |
| RRF Fusion 节点 | 2h | Dev |
| Personalization Rerank 节点 | 4h | Dev |
| Response Generation 节点 | 4h | Dev |

### 10.4 Phase 4: 数据层（第7-8天，与 Phase 3 部分并行）

| 任务 | 工时 | 负责人 |
|------|------|--------|
| 动态 Embedding 生成（模板系统） | 6h | Dev |
| 向量存储 + HNSW 索引管理 | 4h | Dev |
| 全文搜索 GIN 索引管理 | 2h | Dev |
| 数据同步接口（全量/增量） | 4h | Dev |

### 10.5 Phase 5: API 层（第8-10天）

| 任务 | 工时 | 负责人 |
|------|------|--------|
| FastAPI 项目结构 + 中间件 | 4h | Dev |
| /search 接口（SSE 流式） | 6h | Dev |
| /suggest 接口 | 3h | Dev |
| /filters 接口 | 3h | Dev |
| /config 接口 | 2h | Dev |
| /sync 接口 | 2h | Dev |
| 错误处理 + 降级策略 | 2h | Dev |

### 10.6 Phase 6: 前端（第10-13天）

| 任务 | 工时 | 负责人 |
|------|------|--------|
| 项目脚手架 + Tailwind 配置 | 2h | Dev |
| 搜索框组件 + 自动补全 | 6h | Dev |
| 筛选器面板（配置驱动） | 6h | Dev |
| 结果列表 + 卡片（配置驱动） | 6h | Dev |
| 排序栏 + 分页 | 3h | Dev |
| SSE 流式响应处理 | 4h | Dev |
| AI Summary 展示 | 2h | Dev |
| 空状态 + 加载状态 | 2h | Dev |
| 响应式适配 | 2h | Dev |

### 10.7 Phase 7: 集成测试（第14-15天）

| 任务 | 工时 | 负责人 |
|------|------|--------|
| 端到端测试 | 4h | Dev |
| 性能测试（百万数据） | 4h | Dev |
| 配置系统测试（多种表结构） | 4h | Dev |
| Bug 修复 + 优化 | 8h | Dev |

**预估总工期: 15个工作日（3周）**

---

## 十一、成本估算

### 11.1 MVP 月度成本

| 项目 | 用量 | 单价 | 月费用 |
|------|------|------|--------|
| **Embedding API** | 100万 tokens | $0.02/百万 | ~$0.02 |
| **LLM API** | 500万 input + 100万 output tokens | $0.15/$0.60/百万 | ~$1.35 |
| **服务器** | 1台 4核8G | ¥200/月 | ~$30 |
| **总计** | | | **~$32/月** |

### 11.2 生产预估（100万搜索/月）

| 项目 | 用量 | 单价 | 月费用 |
|------|------|------|--------|
| **Embedding API** | 1000万 tokens | $0.02/百万 | ~$0.20 |
| **LLM API** | 5000万 input + 1000万 output | $0.15/$0.60/百万 | ~$13.50 |
| **服务器** | 2台 8核16G | ¥800/月 | ~$120 |
| **Redis** | 1台 4核8G | ¥200/月 | ~$30 |
| **总计** | | | **~$164/月** |

---

## 十二、使用指南

### 12.1 快速开始（30秒接入）

```bash
# 1. 启动服务
docker-compose up -d

# 2. 创建极简配置文件 config.yaml
cat > config.yaml << 'EOF'
data_source:
  table: products
EOF

# 3. 初始化（自动发现 Schema、生成配置、创建索引）
python -m ai_search init --config config.yaml

# 4. 完成！访问 http://localhost:3000
```

### 12.2 基础配置（5分钟调优）

```yaml
# config.yaml — 基础配置
data_source:
  table: products

fields:
  title:
    weight: 1.2              # 提升标题权重
  description:
    weight: 0.8              # 降低描述权重
  brand:
    facetable: true           # 品牌作为面过滤
  price:
    filterable: true          # 价格可筛选

search:
  weights:
    vector: 0.6               # 提升向量搜索权重
    fulltext: 0.2

presentation:
  result_template: card
  fields_order:               # 调整展示顺序
    - image_url
    - title
    - brand
    - price
    - rating
```

### 12.3 高级配置（可选）

```yaml
# config.yaml — 高级配置
data_source:
  table: products

fields:
  title:
    weight: 1.2
    display_name: "商品名称"   # 自定义中文展示名
  specifications:
    type: json
    json_path: "color,material"  # 只提取 JSON 中的 color 和 material
    weight: 0.3

search:
  embedding:
    template: ecommerce_custom
    custom_template:
      formatting: "品名：{title}，品牌：{brand}，类别：{category}。{description}"
  synonyms:                   # 同义词词典
    - ["手机", "移动电话", "智能手机"]
    - ["T恤", "短袖", "T-shirt"]
  stopwords: ["的", "了", "和", "是"]  # 停用词

presentation:
  card_layout:
    image_position: left       # 图片在左侧
    badges:
      - field: brand
        style: "outline"
      - field: category
        style: "filled"
  empty_state:
    title: "抱歉，没有找到相关商品"
    subtitle: "试试调整筛选条件，或联系我们"
```

### 12.4 编程方式接入

```python
from ai_search import SearchEngine

# 方式1: 从 YAML 配置
engine = SearchEngine.from_yaml("config.yaml")

# 方式2: 从字典配置
engine = SearchEngine.from_dict({
    "data_source": {"table": "products"},
    "fields": {"title": {"weight": 1.5}}
})

# 方式3: 极简（自动发现所有配置）
engine = SearchEngine.create(
    db_url="postgresql://user:pass@localhost/db",
    table="products"
)

# 启动 API 服务
engine.serve(port=8000)

# 或编程方式搜索
results = await engine.search(
    query="蓝色运动T恤",
    filters={"price": {"lte": 200}},
    user_id=123
)
```

---

## 十三、边界与限制

### 13.1 适用场景 ✅

| 数据类型 | 适配度 | 说明 |
|----------|--------|------|
| 电商商品表 | ⭐⭐⭐⭐⭐ | 完美适配，预定义模板 |
| 文章内容/博客 | ⭐⭐⭐⭐⭐ | 很好适配，预定义模板 |
| 用户信息/简历 | ⭐⭐⭐⭐ | 很好适配，预定义模板 |
| 产品文档/知识库 | ⭐⭐⭐⭐ | 支持分块策略 |
| 评论/反馈数据 | ⭐⭐⭐ | 需自定义模板 |
| 新闻/资讯数据 | ⭐⭐⭐⭐ | 很好适配 |

### 13.2 数据规模建议

| 数据量 | 体验 | 备注 |
|--------|------|------|
| < 1万条 | ⚡ 极速 | 所有索引驻留内存 |
| 1万 - 50万条 | 🚀 很快 | HNSW 优化即可 |
| 50万 - 500万条 | ✅ 良好 | 需连接池优化 |
| 500万 - 1000万条 | ⚠️ 可接受 | 需分区 + 调优 |
| > 1000万条 | ❌ 不建议 | 需专用架构 |

### 13.3 明确的不适用范围 ❌

1. **纯数值/关系型流水表** — 没有文本内容可供语义搜索
2. **时序数据分析** — 需要 OLAP 聚合，非搜索场景
3. **图遍历查询** — 需要图数据库
4. **实时性要求 < 50ms** — LLM 调用延迟无法满足
5. **字段数 > 100 的超宽表** — 配置复杂度过高

---

*本方案基于 15 维度深度研究（220+ 次搜索、150+ 权威来源）和交叉验证，已整合通用化配置层设计。等待确认后进入开发阶段。*
