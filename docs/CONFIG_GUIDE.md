# PandaSearch 配置指南

> 从 30 秒极简到 30 分钟高级配置

## 快速导航

| 配置级别 | 所需时间 | 覆盖场景 | 文档 |
|---------|---------|---------|------|
| **极简模式** | 30 秒 | ~60% | [configs/minimal.yaml](../configs/minimal.yaml) |
| **基础配置** | 5 分钟 | ~25% | [configs/basic.yaml](../configs/basic.yaml) |
| **高级配置** | 30 分钟 | ~12% | [configs/advanced.yaml](../configs/advanced.yaml) |

## 极简模式（30 秒）

```yaml
data_source:
  table: products
```

系统会自动：
1. 扫描表结构
2. 推断字段类型和权重
3. 生成 Embedding 策略
4. 创建索引
5. 启动搜索服务

## 基础配置（5 分钟）

在极简基础上微调字段权重、搜索策略、UI 展示。

## 高级配置（30 分钟）

完全控制所有配置项，包括自定义模板、同义词、停用词等。

## 完整配置 Schema 参考

详见 [SPEC.md](SPEC.md) 第四章「通用配置层设计」。
