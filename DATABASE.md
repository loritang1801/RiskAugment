# 数据库设计文档

完整的数据库架构、表设计、索引和初始化说明。

## 数据库概览

- **数据库系统**: PostgreSQL 12+
- **向量扩展**: pgvector
- **字符编码**: UTF-8
- **时区**: UTC

## 表设计

### 1. sys_user (系统用户表)

存储系统用户信息。

```sql
CREATE TABLE sys_user (
  id VARCHAR(36) PRIMARY KEY,
  username VARCHAR(50) NOT NULL UNIQUE,
  email VARCHAR(100) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  role VARCHAR(20) NOT NULL DEFAULT 'REVIEWER',
  status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  last_login_at TIMESTAMP
);
```

**字段说明**:
- `id`: 用户唯一标识
- `username`: 用户名，唯一
- `email`: 邮箱，唯一
- `password_hash`: 密码哈希值
- `role`: 用户角色 (ADMIN, REVIEWER, ANALYST)
- `status`: 用户状态 (ACTIVE, INACTIVE, SUSPENDED)
- `created_at`: 创建时间
- `updated_at`: 更新时间
- `last_login_at`: 最后登录时间

**索引**:
```sql
CREATE INDEX idx_user_username ON sys_user(username);
CREATE INDEX idx_user_email ON sys_user(email);
CREATE INDEX idx_user_status ON sys_user(status);
```

---

### 2. risk_case (风险案件表)

存储风险案件信息。

```sql
CREATE TABLE risk_case (
  id VARCHAR(36) PRIMARY KEY,
  transaction_id VARCHAR(100) NOT NULL UNIQUE,
  status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
  risk_level VARCHAR(20) NOT NULL DEFAULT 'MEDIUM',
  country VARCHAR(10) NOT NULL,
  amount DECIMAL(15, 2) NOT NULL,
  description TEXT,
  created_by VARCHAR(36) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (created_by) REFERENCES sys_user(id)
);
```

**字段说明**:
- `id`: 案件唯一标识
- `transaction_id`: 交易 ID，唯一
- `status`: 案件状态 (PENDING, APPROVED, REJECTED)
- `risk_level`: 风险等级 (LOW, MEDIUM, HIGH, CRITICAL)
- `country`: 国家代码
- `amount`: 交易金额
- `description`: 案件描述
- `created_by`: 创建者 ID
- `created_at`: 创建时间
- `updated_at`: 更新时间

**索引**:
```sql
CREATE INDEX idx_case_status ON risk_case(status);
CREATE INDEX idx_case_risk_level ON risk_case(risk_level);
CREATE INDEX idx_case_country ON risk_case(country);
CREATE INDEX idx_case_created_at ON risk_case(created_at DESC);
CREATE INDEX idx_case_transaction_id ON risk_case(transaction_id);
```

---

### 3. ai_decision_record (AI 决策记录表)

存储 AI 分析和决策结果。

```sql
CREATE TABLE ai_decision_record (
  id VARCHAR(36) PRIMARY KEY,
  case_id VARCHAR(36) NOT NULL,
  prompt_version VARCHAR(20) NOT NULL,
  risk_score DECIMAL(3, 2) NOT NULL,
  decision VARCHAR(20) NOT NULL,
  reasoning TEXT NOT NULL,
  similar_cases JSONB,
  execution_time INTEGER NOT NULL,
  tokens_used INTEGER,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (case_id) REFERENCES risk_case(id) ON DELETE CASCADE
);
```

**字段说明**:
- `id`: 记录唯一标识
- `case_id`: 关联的案件 ID
- `prompt_version`: 使用的 Prompt 版本
- `risk_score`: 风险评分 (0-1)
- `decision`: AI 决策 (APPROVE, REJECT, REVIEW)
- `reasoning`: 决策理由
- `similar_cases`: 相似案例 JSON 数据
- `execution_time`: 执行时间（毫秒）
- `tokens_used`: 使用的 Token 数
- `created_at`: 创建时间

**索引**:
```sql
CREATE INDEX idx_ai_case_id ON ai_decision_record(case_id);
CREATE INDEX idx_ai_prompt_version ON ai_decision_record(prompt_version);
CREATE INDEX idx_ai_created_at ON ai_decision_record(created_at DESC);
```

---

### 4. prompt_template (Prompt 模板表)

存储 Prompt 版本信息。

```sql
CREATE TABLE prompt_template (
  id VARCHAR(36) PRIMARY KEY,
  version VARCHAR(20) NOT NULL UNIQUE,
  name VARCHAR(100) NOT NULL,
  description TEXT,
  content TEXT NOT NULL,
  is_active BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  activated_at TIMESTAMP
);
```

**字段说明**:
- `id`: 模板唯一标识
- `version`: 版本号 (v1, v2, v3...)
- `name`: 版本名称
- `description`: 版本描述
- `content`: Prompt 内容
- `is_active`: 是否为活跃版本
- `created_at`: 创建时间
- `updated_at`: 更新时间
- `activated_at`: 激活时间

**索引**:
```sql
CREATE INDEX idx_prompt_version ON prompt_template(version);
CREATE INDEX idx_prompt_is_active ON prompt_template(is_active);
```

---

### 5. case_audit_log (案件审计日志表)

记录案件的所有操作。

```sql
CREATE TABLE case_audit_log (
  id VARCHAR(36) PRIMARY KEY,
  case_id VARCHAR(36) NOT NULL,
  action VARCHAR(50) NOT NULL,
  operator_id VARCHAR(36),
  old_value JSONB,
  new_value JSONB,
  details TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (case_id) REFERENCES risk_case(id) ON DELETE CASCADE,
  FOREIGN KEY (operator_id) REFERENCES sys_user(id)
);
```

**字段说明**:
- `id`: 日志唯一标识
- `case_id`: 关联的案件 ID
- `action`: 操作类型 (CREATE, UPDATE, ANALYZE, APPROVE, REJECT)
- `operator_id`: 操作者 ID
- `old_value`: 修改前的值
- `new_value`: 修改后的值
- `details`: 操作详情
- `created_at`: 操作时间

**索引**:
```sql
CREATE INDEX idx_audit_case_id ON case_audit_log(case_id);
CREATE INDEX idx_audit_action ON case_audit_log(action);
CREATE INDEX idx_audit_created_at ON case_audit_log(created_at DESC);
```

---

### 6. ai_prompt_log (AI 调用日志表)

记录 AI 服务的调用详情。

```sql
CREATE TABLE ai_prompt_log (
  id VARCHAR(36) PRIMARY KEY,
  case_id VARCHAR(36) NOT NULL,
  prompt_version VARCHAR(20) NOT NULL,
  prompt_text TEXT NOT NULL,
  llm_response TEXT NOT NULL,
  retrieved_cases JSONB,
  execution_time INTEGER NOT NULL,
  tokens_used INTEGER,
  cost DECIMAL(10, 4),
  status VARCHAR(20) NOT NULL DEFAULT 'SUCCESS',
  error_message TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (case_id) REFERENCES risk_case(id) ON DELETE CASCADE
);
```

**字段说明**:
- `id`: 日志唯一标识
- `case_id`: 关联的案件 ID
- `prompt_version`: 使用的 Prompt 版本
- `prompt_text`: 实际使用的 Prompt 文本
- `llm_response`: LLM 的响应
- `retrieved_cases`: 检索到的相似案例
- `execution_time`: 执行时间（毫秒）
- `tokens_used`: 使用的 Token 数
- `cost`: 调用成本
- `status`: 调用状态 (SUCCESS, FAILED, TIMEOUT)
- `error_message`: 错误信息
- `created_at`: 创建时间

**索引**:
```sql
CREATE INDEX idx_ai_log_case_id ON ai_prompt_log(case_id);
CREATE INDEX idx_ai_log_version ON ai_prompt_log(prompt_version);
CREATE INDEX idx_ai_log_status ON ai_prompt_log(status);
CREATE INDEX idx_ai_log_created_at ON ai_prompt_log(created_at DESC);
```

---

### 7. knowledge_document (知识库文档表)

存储知识库文档和向量。

```sql
CREATE TABLE knowledge_document (
  id VARCHAR(36) PRIMARY KEY,
  case_id VARCHAR(36) NOT NULL,
  title VARCHAR(255) NOT NULL,
  content TEXT NOT NULL,
  embedding vector(1024),
  metadata JSONB,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (case_id) REFERENCES risk_case(id) ON DELETE CASCADE
);
```

**字段说明**:
- `id`: 文档唯一标识
- `case_id`: 关联的案件 ID
- `title`: 文档标题
- `content`: 文档内容
- `embedding`: 向量表示（1024 维）
- `metadata`: 元数据 JSON
- `created_at`: 创建时间

**索引**:
```sql
CREATE INDEX idx_knowledge_case_id ON knowledge_document(case_id);
CREATE INDEX idx_knowledge_embedding ON knowledge_document USING ivfflat (embedding vector_cosine_ops);
```

---

## 向量索引配置

### IVFFlat 索引

用于高效的向量相似度查询：

```sql
-- 创建 pgvector 扩展
CREATE EXTENSION IF NOT EXISTS vector;

-- 创建向量索引
CREATE INDEX idx_knowledge_embedding ON knowledge_document 
USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);

-- 查询相似文档
SELECT id, title, 1 - (embedding <=> query_embedding) as similarity
FROM knowledge_document
ORDER BY embedding <=> query_embedding
LIMIT 5;
```

### 索引参数说明

- `lists`: 聚类数量，通常设置为 `sqrt(总行数)`
- `vector_cosine_ops`: 使用余弦距离
- 其他距离度量: `vector_l2_ops` (欧氏距离), `vector_ip_ops` (内积)

---

## 数据初始化

### 初始化脚本

```bash
# 创建数据库
createdb risk_control_platform

# 初始化表结构
psql risk_control_platform < src/main/resources/db/init.sql

# 加载模拟数据
python ai-service/scripts/load_mock_data.py
```

### 初始数据

1. **默认用户**:
   - admin / admin123 (ADMIN)
   - reviewer1 / admin123 (REVIEWER)
   - analyst1 / admin123 (ANALYST)

2. **默认 Prompt 版本**:
   - v1: 基础版本
   - v2: 优化版本
   - v3: 增强版本

3. **模拟案件**: 1000 条

---

## 性能优化

### 查询优化

1. **案件列表查询**:
```sql
-- 使用复合索引
CREATE INDEX idx_case_status_created ON risk_case(status, created_at DESC);

-- 查询示例
SELECT * FROM risk_case 
WHERE status = 'PENDING' 
ORDER BY created_at DESC 
LIMIT 20;
```

2. **AI 决策查询**:
```sql
-- 按 Prompt 版本分组统计
SELECT prompt_version, COUNT(*) as count, AVG(risk_score) as avg_score
FROM ai_decision_record
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY prompt_version;
```

### 缓存策略

1. **Redis 缓存**:
   - 案件详情: 1 小时
   - Prompt 版本: 24 小时
   - 统计数据: 1 小时

2. **缓存键格式**:
   - `case:{caseId}`: 案件详情
   - `prompt:{version}`: Prompt 版本
   - `analytics:{type}:{date}`: 统计数据

---

## 备份和恢复

### 备份

```bash
# 完整备份
pg_dump risk_control_platform > backup.sql

# 压缩备份
pg_dump risk_control_platform | gzip > backup.sql.gz

# 定时备份（每天凌晨 2 点）
0 2 * * * pg_dump risk_control_platform | gzip > /backups/backup_$(date +\%Y\%m\%d).sql.gz
```

### 恢复

```bash
# 从备份恢复
psql risk_control_platform < backup.sql

# 从压缩备份恢复
gunzip -c backup.sql.gz | psql risk_control_platform
```

---

## 监控和维护

### 常用查询

```sql
-- 查看表大小
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- 查看索引使用情况
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;

-- 查看慢查询
SELECT query, calls, mean_time, max_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

### 维护任务

```sql
-- 分析表统计信息
ANALYZE risk_case;

-- 重建索引
REINDEX TABLE risk_case;

-- 清理死元组
VACUUM ANALYZE risk_case;
```

---

## 数据一致性

### 外键约束

所有关联表都使用外键约束确保数据一致性：

```sql
-- 案件删除时级联删除相关记录
ALTER TABLE ai_decision_record 
ADD CONSTRAINT fk_case_id 
FOREIGN KEY (case_id) REFERENCES risk_case(id) ON DELETE CASCADE;
```

### 事务隔离级别

使用 `READ_COMMITTED` 隔离级别（默认）确保数据一致性。

---

## 扩展性考虑

### 分区策略

对于大表（如 `ai_prompt_log`），可以按时间分区：

```sql
-- 按月分区
CREATE TABLE ai_prompt_log_2024_02 PARTITION OF ai_prompt_log
FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');
```

### 读写分离

在生产环境中，可以配置主从复制：

```
主库 (写入) -> 从库 (读取)
```

---

## 故障排查

### 常见问题

1. **查询缓慢**:
   - 检查索引是否被使用
   - 运行 `ANALYZE` 更新统计信息
   - 考虑添加新索引

2. **磁盘空间不足**:
   - 清理旧数据
   - 压缩表和索引
   - 扩展磁盘容量

3. **连接数过多**:
   - 检查应用连接池配置
   - 增加 `max_connections` 参数
   - 使用连接池（如 PgBouncer）
