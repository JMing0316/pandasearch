# PandaSearch 精简版 MVP 实施计划

> 目标：砍掉 Agent 层，实现"无 Agent 的混合搜索"，让搜索真正跑起来。
> 策略：固定执行 SQL 预过滤 → 向量搜索 + 全文搜索 → RRF 融合 → 返回结果

---

## 当前状态

| 模块 | 完成度 | 状态 |
|------|--------|------|
| 五层配置模型 | 100% | ✅ Pydantic 模型完整 |
| Schema 自动发现 | 100% | ✅ 15 条分类规则 |
| 数据库连接 | 100% | ✅ asyncpg 连接池 |
| FastAPI 框架 | 50% | ⚠️ 端点存在，逻辑为 TODO |
| 前端布局 | 40% | ⚠️ SearchBox 可用，其余占位 |
| **Embedding 生成** | **0%** | ❌ 未实现 |
| **向量存储/索引** | **0%** | ❌ 未实现 |
| **向量检索** | **0%** | ❌ 未实现 |
| **全文检索** | **0%** | ❌ 未实现 |
| **RRF 融合** | **0%** | ❌ 未实现 |
| **Agent 编排** | **0%** | ❌ 本次跳过 |

---

## 实施阶段

### Stage 1: 基础设施检查与准备（Orchestrator）

- 检查 Python 环境、依赖安装
- 检查 Docker 环境
- 确认 .env 配置

### Stage 2: Embedding 与索引层（Worker_A）

**任务：** 实现向量生成、存储、索引创建

**文件：**
- `backend/pandasearch/embedding.py` — OpenAI Embedding 生成
- `backend/pandasearch/index_manager.py` — 向量表创建、HNSW 索引、GIN 索引、数据同步

**关键逻辑：**
1. 根据配置的组合策略，将多个文本字段拼接成 Embedding 输入
2. 调用 OpenAI `text-embedding-3-small` 生成 1536 维向量
3. 创建 `{table}_embeddings` 表（含 vector 列）
4. 创建 HNSW 索引（m=16, ef=64）
5. 创建 GIN 全文索引（在组合文本列上）
6. 全量/增量同步接口

### Stage 3: 搜索管道核心（Worker_B）

**任务：** 实现混合搜索 + RRF 融合

**文件：**
- `backend/pandasearch/search_pipeline.py` — 完整搜索管道

**关键逻辑：**
1. **Query 预处理** — 简单分词、去除停用词
2. **SQL 预过滤** — 根据 filters 构建 WHERE 子句
3. **向量搜索** — `SELECT ... ORDER BY embedding <=> $1 LIMIT 50`
4. **全文搜索** — `SELECT ... WHERE to_tsvector(...) @@ plainto_tsquery(...)`
5. **RRF 融合** — `score = Σ 1/(k + rank)`，k=60
6. **返回 Top N**

### Stage 4: API 层完善（Worker_C）

**任务：** 完善所有 API 端点

**文件：**
- `backend/pandasearch/main.py` — 更新端点
- `backend/pandasearch/api_models.py` — 请求/响应 Pydantic 模型

**端点：**
- `POST /api/v1/search` — 完整搜索（非 SSE，先同步）
- `GET /api/v1/suggest` — 自动补全（基于前缀匹配）
- `GET /api/v1/filters` — 筛选器选项（基于数据聚合）
- `GET /api/v1/config` — 当前配置
- `POST /api/v1/sync` — 索引同步

### Stage 5: 前端组件实现（Worker_D）

**任务：** 实现前端核心组件

**文件：**
- `frontend/pandasearch-ui/src/components/ResultCard/ResultCard.tsx` — 配置驱动的结果卡片
- `frontend/pandasearch-ui/src/components/ResultList/ResultList.tsx` — 结果列表
- `frontend/pandasearch-ui/src/components/FilterPanel/FilterPanel.tsx` — 动态筛选器
- `frontend/pandasearch-ui/src/components/SortBar/SortBar.tsx` — 排序栏（使用配置中的 sort_options）
- `frontend/pandasearch-ui/src/hooks/useSearch.ts` — 搜索 Hook
- `frontend/pandasearch-ui/src/App.tsx` — 更新主应用

### Stage 6: 集成测试与验证（Orchestrator）

- 启动 Docker 环境
- 创建测试数据表
- 运行初始化流程
- 执行搜索验证
- 前端联调

---

## 关键设计决策

| 决策 | 选择 | 理由 |
|------|------|------|
| Agent 层 | **跳过** | 最复杂，MVP 阶段固定策略足够 |
| 搜索策略 | 固定 Hybrid | 向量 0.5 + 全文 0.3 + SQL 0.2 |
| 响应方式 | 同步 JSON | SSE 流式后置，先保证功能可用 |
| Embedding | OpenAI API | 依赖已安装，$0.02/百万 token |
| 向量维度 | 1536 | text-embedding-3-small 默认 |
| RRF k | 60 | 业界标准 |
| 个性化 | 跳过 | MVP 阶段不做用户行为加权 |
| 缓存 | 跳过 | Redis 已连接但先不用 |

---

## 文件变更清单

### 新增文件
- `backend/pandasearch/embedding.py`
- `backend/pandasearch/index_manager.py`
- `backend/pandasearch/search_pipeline.py`
- `backend/pandasearch/api_models.py`
- `frontend/pandasearch-ui/src/hooks/useSearch.ts`
- `frontend/pandasearch-ui/src/types/search.ts`

### 修改文件
- `backend/pandasearch/search_engine.py` — 接入搜索管道
- `backend/pandasearch/main.py` — 完善端点
- `backend/pandasearch/config.py` — 可能需要微调
- `frontend/pandasearch-ui/src/App.tsx`
- `frontend/pandasearch-ui/src/components/ResultCard/ResultCard.tsx`
- `frontend/pandasearch-ui/src/components/ResultList/ResultList.tsx`
- `frontend/pandasearch-ui/src/components/FilterPanel/FilterPanel.tsx`
- `frontend/pandasearch-ui/src/components/SortBar/SortBar.tsx`
- `frontend/pandasearch-ui/src/components/SearchBox/SearchBox.tsx`

---

## 成功标准

1. ✅ 能对新表执行 `init` 命令，自动创建索引
2. ✅ `POST /api/v1/search?q=xxx` 返回真实搜索结果（非空）
3. ✅ 结果包含：id、title、score、高亮片段
4. ✅ 前端能展示搜索结果卡片
5. ✅ 筛选器面板能展示可用筛选选项
6. ✅ 排序功能可用

---

*计划制定时间: 2026-06-10*
*预计执行: 分阶段并行推进*
