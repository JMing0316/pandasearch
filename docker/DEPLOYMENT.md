# PandaSearch Docker 部署指南

> 物理机运行 PostgreSQL，Redis + 后端 + 前端 全部容器化

---

## 📐 部署架构

```
┌─────────────────────────────────────────┐
│              物理机 (宿主机)               │
│  ┌─────────────────────────────────────┐ │
│  │  PostgreSQL 16 + pgvector          │ │
│  │  端口: 5432                         │ │
│  └─────────────────────────────────────┘ │
│                                         │
│  ┌─────────┐ ┌──────────┐ ┌──────────┐ │
│  │  Redis  │ │ Backend  │ │ Frontend │ │
│  │ :6379   │ │ :8000    │ │ :3000    │ │
│  └─────────┘ └──────────┘ └──────────┘ │
│     Docker Compose 容器网络               │
└─────────────────────────────────────────┘
```

| 组件 | 部署方式 | 访问地址 |
|------|---------|---------|
| PostgreSQL | 物理机 | `localhost:5432` |
| Redis | Docker 容器 | `localhost:6379` |
| 后端 (FastAPI) | Docker 容器 | `http://localhost:8000` |
| 前端 (React) | Docker 容器 | `http://localhost:3000` |

---

## ✅ 前置条件

1. **Docker Desktop** 已安装并运行
2. **PostgreSQL 16** 已在物理机上运行，且：
   - 端口 `5432` 可访问
   - 数据库 `lawwit_db` 已创建
   - 用户 `postgres` / 密码 `users` 可登录
   - **pgvector 扩展已安装**（`CREATE EXTENSION vector;`）
3. 项目根目录存在 `.env` 文件（包含 `OPENAI_API_KEY`）

---

## 🚀 一键部署

### 步骤 1：进入 docker 目录

```bash
cd D:/project/pandasearch/docker
```

### 步骤 2：构建并启动容器

```bash
docker-compose up -d --build
```

参数说明：
- `-d`：后台运行
- `--build`：强制重新构建镜像（首次部署必须）

### 步骤 3：查看运行状态

```bash
docker-compose ps
```

预期输出：
```
NAME                    IMAGE                           STATUS          PORTS
pandasearch-backend     docker-backend                  Up              0.0.0.0:8000->8000/tcp
pandasearch-frontend    docker-frontend                 Up              0.0.0.0:3000->3000/tcp
pandasearch-redis       redis:7-alpine                  Up              0.0.0.0:6379->6379/tcp
```

### 步骤 4：验证服务

```bash
# 后端健康检查
curl http://localhost:8000/health

# Redis 检查
docker exec pandasearch-redis redis-cli ping
# 预期输出: PONG
```

---

## 🔧 常用运维命令

| 操作 | 命令 |
|------|------|
| 查看日志 | `docker-compose logs -f backend` |
| 重启服务 | `docker-compose restart backend` |
| 停止所有容器 | `docker-compose down` |
| 停止并删除数据卷 | `docker-compose down -v` |
| 进入后端容器 | `docker exec -it pandasearch-backend bash` |
| 进入 Redis 容器 | `docker exec -it pandasearch-redis sh` |

---

## ⚙️ 环境变量说明

### 物理机 PostgreSQL 连接

Docker 中的后端通过 `host.docker.internal` 访问宿主机上的 PostgreSQL：

```yaml
# docker-compose.yml 中已配置
DATABASE_URL=postgresql+asyncpg://postgres:users@host.docker.internal:5432/lawwit_db
```

> **Windows Docker Desktop**：`host.docker.internal` 自动解析，无需额外配置。
>
> **Linux Docker**：若 `host.docker.internal` 不可用，请将后端 `DATABASE_URL` 中的 `host.docker.internal` 替换为宿主机实际 IP 地址。

### 容器间 Redis 连接

```yaml
# docker-compose.yml 中已配置
REDIS_URL=redis://redis:6379/0
```

`redis` 是 Docker Compose 内部网络中的服务名，容器间通过服务名自动解析。

### 前端 API 地址

```yaml
# docker-compose.yml 中已配置
VITE_API_URL=http://localhost:8000
```

浏览器访问前端 `http://localhost:3000` 时，API 请求会发送到宿主机的 `8000` 端口（后端容器映射）。

---

## 📁 已修改的文件清单

| 文件 | 修改内容 |
|------|---------|
| `docker/docker-compose.yml` | 移除 db 服务，添加容器名、网络、重启策略，调整服务顺序 |
| `frontend/pandasearch-ui/Dockerfile` | 显式安装 `serve`，避免 `npx` 运行时下载 |

---

## 🐛 常见问题

### Q1: 后端无法连接 PostgreSQL

**现象**：后端日志报错 `Connection refused`

**排查**：
1. 确认 PostgreSQL 正在运行且监听 `0.0.0.0:5432`（不仅是 `127.0.0.1`）
2. 检查防火墙是否放行 5432 端口
3. 在宿主机测试连接：`psql -h localhost -p 5432 -U postgres -d lawwit_db`

### Q2: 前端页面空白或 API 报错

**现象**：浏览器控制台显示 `Failed to fetch`

**排查**：
1. 确认后端已启动：`curl http://localhost:8000/health`
2. 确认前端 `VITE_API_URL` 指向的是浏览器能访问的地址（`localhost:8000`）
3. 检查浏览器是否开启了跨域拦截插件

### Q3: 修改后端代码后如何生效

由于 `docker-compose.yml` 中挂载了 `../backend/pandasearch:/app/pandasearch`，代码修改会自动同步到容器内。

但 Python 是解释型语言，**需要重启后端容器才能重新加载**：

```bash
docker-compose restart backend
```

### Q4: 如何更新依赖后重新构建

```bash
docker-compose down
docker-compose up -d --build
```

---

## 📌 访问地址汇总

| 服务 | URL | 说明 |
|------|-----|------|
| 前端页面 | http://localhost:3000 | 搜索界面 |
| 后端 API | http://localhost:8000 | FastAPI 服务 |
| 后端文档 | http://localhost:8000/docs | Swagger UI |
| 健康检查 | http://localhost:8000/health | 服务状态 |

---

*部署配置生成时间: 2025-06-11*
