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

| 分支 | 用途 |
|------|------|
| `main` | 稳定分支，仅合并已测试的代码 |
| `dev` | 开发分支，日常开发基于此 |
| `feature/*` | 功能分支 |
| `bugfix/*` | 修复分支 |

## 提交规范

```
feat:     新功能
fix:      修复问题
docs:     文档更新
style:    代码格式（不影响功能）
refactor: 重构
test:     测试相关
chore:    构建/工具相关
perf:     性能优化
ci:       CI/CD 相关
```

## Pull Request 流程

1. 从 `dev` 分支创建功能分支
2. 开发完成后提交 PR 到 `dev`
3. 确保 CI 通过
4. 至少 1 人 Code Review 后合并
