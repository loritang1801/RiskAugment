# 风控决策增强平台 (Risk Control Platform)

一个基于 AI 和 RAG 的智能风险控制决策平台，支持实时案件分析、Prompt 版本管理、完整的审计追溯和数据分析。

## 📋 项目概述

风控决策增强平台是一个企业级的风险管理系统，集成了：
- **AI 驱动的决策**：使用 LLM 和 RAG 进行智能风险分析
- **完整的审计追溯**：记录所有操作和 AI 调用日志
- **Prompt 版本管理**：支持多个 Prompt 版本的管理和切换
- **数据分析**：完整的统计和对比分析
- **专业的 UI**：基于 Ant Design Pro 的现代化界面

## 🚀 快速开始

### 前置要求
- Java 11+
- Python 3.8+
- Node.js 14+
- PostgreSQL 12+
- Redis 6+

### 本地开发环境部署

#### 1. 数据库初始化
```bash
# 创建数据库
createdb risk_control_platform

# 初始化表结构
psql risk_control_platform < risk-control-platform/src/main/resources/db/init.sql
```

#### 2. 启动 Java 后端
```bash
cd risk-control-platform
mvn clean install
mvn spring-boot:run
```

#### 3. 启动 Python AI 服务
```bash
cd risk-control-platform/ai-service
pip install -r requirements.txt
python app.py
```

#### 4. 启动前端
```bash
cd risk-control-platform/frontend
npm install
run-vite.bat
```

访问 http://localhost:3000 查看应用

## 📁 项目结构

```
risk-control-platform/
├── src/                          # Java Spring Boot 后端
│   ├── main/java/com/riskcontrol/
│   │   ├── controller/          # API 控制器
│   │   ├── service/             # 业务逻辑
│   │   ├── entity/              # 数据实体
│   │   ├── repository/          # 数据访问
│   │   └── config/              # 配置类
│   └── main/resources/
│       ├── db/init.sql          # 数据库初始化脚本
│       └── application.yml      # 应用配置
├── ai-service/                   # Python Flask AI 服务
│   ├── src/
│   │   ├── agent/               # AI Agent 和 Tool
│   │   ├── api/                 # API 路由
│   │   ├── database/            # 数据库模型
│   │   ├── embedding/           # 向量化模型
│   │   ├── llm/                 # LLM 客户端
│   │   ├── prompt/              # Prompt 管理
│   │   ├── rag/                 # RAG 检索
│   │   └── services/            # 业务服务
│   └── scripts/                 # 数据生成脚本
└── frontend/                     # Vue 3 前端
    ├── src/
    │   ├── views/               # 页面组件
    │   ├── api/                 # API 调用
    │   ├── stores/              # Pinia 状态管理
    │   └── router/              # 路由配置
    └── package.json
```

## 🏗️ 架构设计

### 5 层架构

```
┌─────────────────────────────────────┐
│      前端层 (Vue 3 + Ant Design)    │
├─────────────────────────────────────┤
│    API 层 (Spring Boot REST API)    │
├─────────────────────────────────────┤
│   业务逻辑层 (Service + Agent)      │
├─────────────────────────────────────┤
│   数据访问层 (Repository + ORM)     │
├─────────────────────────────────────┤
│   数据存储层 (PostgreSQL + Redis)   │
└─────────────────────────────────────┘
```

### AI 分析流程

```
案件输入
  ↓
规则引擎查询 (Tool 1)
  ↓
RAG 检索相似案例 (Tool 2)
  ↓
相似案例分析 (Tool 3)
  ↓
交易历史查询 (Tool 4)
  ↓
LLM 综合分析
  ↓
决策输出 + 日志记录
```

## 🔑 核心功能

### 1. 案件管理
- 创建、查看、编辑、删除案件
- 高级筛选（交易ID、状态、风险等级、国家）
- 案件详情展示
- 审计追溯

### 2. AI 分析
- 自动风险评分
- 相似案例检索
- 规则引擎集成
- 交易历史分析
- LLM 决策建议

### 3. Prompt 管理
- 多版本 Prompt 管理
- 版本激活/切换
- 性能指标统计
- 版本对比分析

### 4. 日志和审计
- AI 调用日志记录
- 案件操作审计
- 完整的执行链路追溯
- 时间线展示

### 5. 数据分析
- 审核时间统计
- Override 率统计
- Prompt 版本对比
- 趋势分析图表

## 📊 API 文档

### 案件管理 API
```
GET    /api/cases                    # 获取案件列表
GET    /api/cases/{id}               # 获取案件详情
POST   /api/cases                    # 创建案件
PUT    /api/cases/{id}               # 更新案件
DELETE /api/cases/{id}               # 删除案件
```

### AI 分析 API
```
POST   /api/ai/analyze               # 执行 AI 分析
GET    /api/ai/decision/{id}         # 获取分析结果
```

### Prompt 管理 API
```
GET    /api/prompts                  # 获取所有 Prompt 版本
GET    /api/prompts/{version}        # 获取特定版本
POST   /api/prompts                  # 创建新版本
PUT    /api/prompts/{version}/activate  # 激活版本
```

### 审计日志 API
```
GET    /api/cases/{caseId}/audit-trail      # 获取审计追溯
GET    /api/cases/{caseId}/execution-chain  # 获取执行链路
```

### 分析 API
```
GET    /api/analytics/review-efficiency     # 审核时间统计
GET    /api/analytics/override-rate         # Override 率统计
GET    /api/analytics/prompt-comparison     # Prompt 版本对比
```

## 🗄️ 数据库设计

### 核心表

| 表名 | 说明 |
|------|------|
| sys_user | 系统用户 |
| risk_case | 风险案件 |
| ai_decision_record | AI 决策记录 |
| prompt_template | Prompt 模板 |
| case_audit_log | 案件审计日志 |
| ai_prompt_log | AI 调用日志 |
| knowledge_document | 知识库文档 |

### 关键索引
- `idx_case_status`: 案件状态查询
- `idx_case_risk_level`: 风险等级查询
- `idx_ai_prompt_version`: Prompt 版本查询
- `idx_audit_case_id`: 审计日志查询
- `idx_knowledge_embedding`: 向量相似度查询

## 🔧 技术栈

### 后端
- **框架**: Spring Boot 2.7+
- **ORM**: JPA/Hibernate
- **数据库**: PostgreSQL 12+
- **缓存**: Redis 6+
- **API 文档**: Swagger/OpenAPI

### AI 服务
- **框架**: Flask
- **LLM**: Claude/OpenAI
- **向量化**: BAAI/bge-large-zh-v1.5
- **RAG**: LangChain
- **向量数据库**: pgvector

### 前端
- **框架**: Vue 3
- **UI 库**: Ant Design Vue
- **状态管理**: Pinia
- **图表**: ECharts
- **HTTP 客户端**: Axios

## 📈 性能指标

| 指标 | 目标 | 实际 |
|------|------|------|
| 案件列表查询 | < 500ms | ~300ms |
| 案件详情查询 | < 2s | ~1.5s |
| RAG 检索 | < 500ms | ~400ms |
| LLM 调用 | < 5s | ~3s |
| 完整分析 | < 10s | ~8s |

## 🧪 测试

### 单元测试
```bash
cd risk-control-platform
mvn test
```

### 集成测试
```bash
mvn verify
```

### 前端测试
```bash
cd frontend
npm run lint
npm run type-check
```

## 📝 开发指南

### 添加新的 API 端点

1. 创建 Entity 类
2. 创建 Repository 接口
3. 创建 Service 类
4. 创建 Controller 类
5. 添加 Swagger 注解
6. 编写单元测试

### 添加新的 Tool

1. 继承 Tool 基类
2. 实现 execute() 方法
3. 添加到 get_tools() 函数
4. 编写测试用例

### 添加新的前端页面

1. 创建 Vue 组件
2. 添加路由配置
3. 创建 API 调用函数
4. 集成到导航菜单

## 🚀 部署

### Docker 部署

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### Kubernetes 部署

```bash
# 创建命名空间
kubectl create namespace risk-control

# 部署应用
kubectl apply -f k8s/ -n risk-control

# 查看状态
kubectl get pods -n risk-control
```

## 📚 文档

- [API 文档](./API.md)
- [数据库设计](./DATABASE.md)
- [Prompt 设计](./PROMPT.md)
- [部署指南](./DEPLOYMENT.md)
- [开发指南](./DEVELOPMENT.md)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 👥 团队

- 架构设计: AI Team
- 后端开发: Java Team
- 前端开发: Vue Team
- AI 集成: ML Team

## 📞 联系方式

- 邮箱: support@example.com
- 文档: https://docs.example.com
- 问题追踪: https://github.com/example/issues

## Interview Demo Mode

If you are running this project as a personal demo (without real upstream systems):

- set `AI_DECISION_MODE=llm_only`
- keep `RULE_ENGINE_URL` empty
- keep `TRANSACTION_HISTORY_URL` empty
- set `AGENT_TOOL_ALLOW_FALLBACK=false`

See `QUICK_START.md` for step-by-step startup.
