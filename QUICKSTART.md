# PandaSearch 快速使用指南

> 精简版 MVP 已就绪！以下步骤让你的 PostgreSQL 表拥有 AI 智能搜索能力。

---

## 1. 环境准备

### 1.1 复制环境变量

```bash
cp .env.example .env
# 编辑 .env，填入你的 OPENAI_API_KEY
```

### 1.2 启动基础设施（Docker）

```bash
cd docker
docker-compose up -d redis
```

这会启动：
- PostgreSQL 16 + pgvector（端口 5432）
- Redis 7（端口 6379）

### 1.3 安装后端依赖

```bash
cd backend
pip install -e ".[dev]"
```

### 1.4 安装前端依赖

```bash
cd frontend/pandasearch-ui
npm install
```

---

## 2. 配置你的数据表

### 2.1 创建配置文件

```bash
# 方式1: 极简配置（只填表名）
cat > my_config.yaml << 'EOF'
data_source:
  table: articles
EOF

# 方式2: 完整配置（覆盖排序、展示等）
# 参考 configs/articles.yaml
```

### 2.2 确保表已存在

```sql
-- 示例：文章表
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT,
    author VARCHAR(100),
    category VARCHAR(50),
    tags JSONB,
    published_at TIMESTAMP,
    view_count INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active'
);
```

---

## 3. 初始化搜索索引

### 3.1 启动后端服务

```bash
cd backend
python -m pandasearch.main
# 或
pandasearch
```

### 3.2 调用初始化 API

```bash
curl -X POST http://localhost:8000/api/v1/init
```

这会：
1. ✅ 自动发现 Schema（字段类型、权重）
2. ✅ 创建向量嵌入表 `{table}_embeddings`
3. ✅ 创建 HNSW 向量索引
4. ✅ 创建 GIN 全文索引
5. ✅ 全量生成 Embedding 并同步

**响应示例：**
```json
{
  "status": "ok",
  "embeddings_table": true,
  "hnsw_index": true,
  "fulltext_index": true,
  "sync": {
    "processed": 1000,
    "batches": 10,
    "errors": []
  }
}
```

---

## 4. 开始搜索

### 4.1 API 搜索

```bash
curl -X POST http://localhost:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query": "人工智能发展趋势", "page": 1, "page_size": 10}'
```

**响应示例：**
```json
{
  "results": [
    {
      "id": 42,
      "score": 0.9234,
      "title": "2024年人工智能发展趋势分析",
      "author": "张三",
      "category": "科技",
      "highlights": {
        "title": "<mark>人工智能</mark>发展趋势分析"
      }
    }
  ],
  "total": 156,
  "page": 1,
  "page_size": 10,
  "query": "人工智能发展趋势",
  "took_ms": 245,
  "suggested_filters": [
    {
      "field": "category",
      "type": "multi_select",
      "label": "类别",
      "options": [
        {"value": "科技", "count": 45},
        {"value": "商业", "count": 32}
      ]
    }
  ]
}
```

### 4.2 自动补全

```bash
curl "http://localhost:8000/api/v1/suggest?q=人工&limit=5"
```

### 4.3 筛选器选项

```bash
curl "http://localhost:8000/api/v1/filters"
```

### 4.4 带筛选的搜索

```bash
curl -X POST http://localhost:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "人工智能",
    "filters": {
      "category": "科技",
      "view_count": {"gte": 100}
    }
  }'
```

---

## 5. 启动前端

```bash
cd frontend/pandasearch-ui
npm run dev
```

访问 http://localhost:3000 即可使用搜索界面。

---

## 6. 增量同步

当数据更新后，同步索引：

```bash
# 全量重建
curl -X POST http://localhost:8000/api/v1/sync \
  -d '{"full_rebuild": true}'

# 增量更新指定 ID
curl -X POST http://localhost:8000/api/v1/sync \
  -d '{"item_ids": [1, 2, 3]}'
```

---

## 7. 核心 API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/api/v1/search` | POST | 混合搜索 |
| `/api/v1/suggest` | GET | 自动补全 |
| `/api/v1/filters` | GET | 筛选器选项 |
| `/api/v1/config` | GET | 当前配置 |
| `/api/v1/sync` | POST | 索引同步 |
| `/api/v1/init` | POST | 一键初始化 |

---

## 8. 注意事项

1. **OpenAI API Key** — Embedding 生成需要有效的 OpenAI API Key
2. **pgvector 扩展** — 数据库必须已安装 pgvector 扩展
3. **数据量** — MVP 阶段建议 < 100 万条，同步时间取决于数据量和 API 速率限制
4. **向量维度** — 默认 1536（text-embedding-3-small），可在配置中调整
5. **排序** — 当前仅支持相关性排序，字段排序（如按时间、按阅读量）需后续开发

---

*指南生成时间: 2026-06-10*
