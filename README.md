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

### 1. Redis 与 MySQL

在仓库根目录执行：

```powershell
docker compose up -d redis
```

Redis 使用主机端口 `6380`。检查点依赖 Redis Stack 的扩展能力，不能直接替换成未安装对应模块的普通 Redis。

在本地 MySQL 中创建数据库：

```sql
CREATE DATABASE IF NOT EXISTS plan_db CHARACTER SET utf8mb4;
```

### 2. Spring Boot

确保 `JAVA_HOME` 指向 JDK 21。

```powershell
cd plan-website-backend
$env:DB_USERNAME = "root"
$env:DB_PASSWORD = "your-local-database-password"
mvn spring-boot:run
```

默认服务地址：`http://localhost:8080`；OpenAPI：`http://localhost:8080/v3/api-docs`。
可通过 `SPRING_DATASOURCE_URL` 覆盖数据库地址。邮件参数使用 `MAIL_USERNAME`、`MAIL_PASSWORD`；短信默认关闭，需要启用时配置 `SMS_ENABLED`、`ALIYUN_ACCESS_KEY_ID` 和 `ALIYUN_ACCESS_KEY_SECRET`，并填写业务签名与模板。

### 3. Agent

```powershell
cd plan-agent-service
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

编辑 `.env`，填写自己的 `OPENAI_API_KEY`，按供应商配置 `OPENAI_API_BASE` 与 `OPENAI_MODEL`。随后启动：

```powershell
.\.venv\Scripts\python.exe run.py
```

默认服务地址：`http://localhost:8090`。`.env` 已排除在 Git 之外。

### 4. 前端

```powershell
cd plan-website-frontend
npm ci
npm run dev
```

打开终端显示的地址，默认 `http://localhost:8082`。Vite 将业务请求代理到 8080，将 Agent 请求代理到 8090。

## 开发检查

```powershell
# 在前端目录
npm run build
# 在后端目录
mvn test
# 在 Agent 目录
python -m compileall -q app generated
```

`tests/smoke_*.py` 是依赖外部服务和模型的集成冒烟脚本，执行前需要准备测试用户与服务，可能创建任务并产生模型费用。它们不是完全离线的单元测试。

业务接口发生变化后，在 Agent 虚拟环境安装 `requirements-dev.txt`，运行 `scripts/generate_client.ps1` 重新生成客户端。

## 当前边界

本项目用于学习和本地演示。当前认证实现尚未达到生产要求，包括明文密码处理及部分接口依赖客户端提交用户标识；请勿直接部署为公开服务。排期检查主要针对已落库任务，批量失败后的补偿删除为尽力恢复，不提供分布式事务保证。Redis 重启后的恢复能力取决于持久化配置，检查点也受 TTL 限制。
