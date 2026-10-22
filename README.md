# 智能日程规划 Agent

`plan_agent` — A front-end and back-end schedule planning system with an assistant agent for operation support.

通过自然语言管理任务、生成多日计划，并在人工确认后将计划写入日程。项目包含 Vue 3 前端、Spring Boot 业务服务与基于 LangGraph 的 Python Agent 服务。

## 功能与设计

- **双路径 Agent**：ReAct 组合原子工具处理具体操作，Plan-and-Execute 处理目标拆解和整体排期。
- **业务适配层**：OpenAPI 生成 Python 客户端，BackendGateway 统一处理 DTO 转换、接口异常与敏感字段过滤。
- **校验与修订**：调用业务接口检查已有日程的时间冲突、每日容量、休息间隔和截止时间；将反馈交给规划器进行有限轮次修订。
- **人工确认**：使用 LangGraph interrupt / Command 支持预览、确认、取消及修改后重规划。
- **会话状态**：Redis 保存检查点、会话历史、摘要与待处理动作。
- **界面同步**：Agent 完成操作后通过 SSE 发送变更事件，规划页面重新查询业务数据。

```text
Vue 3 frontend
  |-- /api/* ------> Spring Boot --> MySQL
  |-- /api/ai/* ---> FastAPI / LangGraph --> Redis
                              |
                       BackendGateway
                              |
                     Spring Boot OpenAPI
```

## 目录

```text
plan-agent-service/       Agent、工具、会话存储与生成的 API 客户端
plan-website-backend/     Java 业务接口、排期校验与数据模型
plan-website-frontend/    Vue 3 页面与聊天面板
docker-compose.yml       本地 Redis Stack
```
`generated/plan_api_client` 是运行依赖，保留在仓库中；依赖目录、编译产物、日志和本地凭据不提交。

## 本地启动

准备 Python 3.11+、JDK 21、Maven、Node.js 20+、MySQL 8 和 Docker。以下命令在 PowerShell 中运行，三个服务分别使用独立终端。

## 当前边界

本项目用于学习和本地演示。当前认证实现尚未达到生产要求，包括明文密码处理及部分接口依赖客户端提交用户标识；请勿直接部署为公开服务。排期检查主要针对已落库任务，批量失败后的补偿删除为尽力恢复，不提供分布式事务保证。Redis 重启后的恢复能力取决于持久化配置，检查点也受 TTL 限制。
