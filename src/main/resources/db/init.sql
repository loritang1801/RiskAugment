-- Risk Control Platform Database Initialization Script

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- 1. sys_user 表 - 系统用户表
-- ============================================================================
CREATE TABLE IF NOT EXISTS sys_user (
    id BIGSERIAL PRIMARY KEY,
    
    -- 用户信息
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    
    -- 角色和权限
    role VARCHAR(20) NOT NULL,  -- ADMIN, REVIEWER, ANALYST
    department VARCHAR(100),
    
    -- 状态
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',  -- ACTIVE, INACTIVE, LOCKED
    last_login_at TIMESTAMP,
    
    -- 系统字段
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    version INT NOT NULL DEFAULT 0
);

-- 索引
CREATE UNIQUE INDEX IF NOT EXISTS idx_user_username ON sys_user(username);
CREATE UNIQUE INDEX IF NOT EXISTS idx_user_email ON sys_user(email);
CREATE INDEX IF NOT EXISTS idx_user_role ON sys_user(role);
CREATE INDEX IF NOT EXISTS idx_user_status ON sys_user(status);
CREATE INDEX IF NOT EXISTS idx_user_created_at ON sys_user(created_at);

-- 注释
COMMENT ON TABLE sys_user IS '系统用户表';
COMMENT ON COLUMN sys_user.username IS '用户名';
COMMENT ON COLUMN sys_user.role IS '用户角色';

-- ============================================================================
-- 2. risk_case 表 - 风险案件表
-- ============================================================================
CREATE TABLE IF NOT EXISTS risk_case (
    id BIGSERIAL PRIMARY KEY,
    
    -- 业务标识
    biz_transaction_id VARCHAR(64) NOT NULL UNIQUE,
    
    -- 交易信息
    amount DECIMAL(18,2) NOT NULL,
    currency VARCHAR(10) NOT NULL,
    
    -- 提取的关键字段（便于查询）
    country VARCHAR(10),
    device_risk VARCHAR(20),  -- LOW, MEDIUM, HIGH
    user_label VARCHAR(50),   -- new_user, existing_user, vip_user
    
    -- 风险特征快照（JSONB）
    risk_features JSONB NOT NULL,
    
    -- 规则引擎输出
    rule_engine_score DECIMAL(5,2),
    triggered_rules JSONB,  -- ["RULE_001", "RULE_005"]
    
    -- 综合风险评分
    risk_score DECIMAL(5,2),
    risk_level VARCHAR(20),  -- LOW, MEDIUM, HIGH
    
    -- 案件状态
    risk_status VARCHAR(30) NOT NULL,  -- PENDING, ANALYZING, APPROVED, REJECTED
    
    -- AI 决策关联
    ai_decision_id BIGINT,
    
    -- 最终人工决策
    final_decision VARCHAR(20),  -- APPROVE, REJECT
    reviewer_id BIGINT,
    user_id BIGINT,
    
    -- 系统字段
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    version INT NOT NULL DEFAULT 0,
    
    -- 外键
    CONSTRAINT fk_case_reviewer FOREIGN KEY (reviewer_id) REFERENCES sys_user(id)
);

-- 索引
CREATE UNIQUE INDEX IF NOT EXISTS idx_case_biz_id ON risk_case(biz_transaction_id);
CREATE INDEX IF NOT EXISTS idx_case_status ON risk_case(risk_status);
CREATE INDEX IF NOT EXISTS idx_case_risk_level ON risk_case(risk_level);
CREATE INDEX IF NOT EXISTS idx_case_created_at ON risk_case(created_at);
CREATE INDEX IF NOT EXISTS idx_case_reviewer_id ON risk_case(reviewer_id);
CREATE INDEX IF NOT EXISTS idx_case_user_id ON risk_case(user_id);
CREATE INDEX IF NOT EXISTS idx_case_country ON risk_case(country);
CREATE INDEX IF NOT EXISTS idx_case_device_risk ON risk_case(device_risk);
CREATE INDEX IF NOT EXISTS idx_case_user_label ON risk_case(user_label);
CREATE INDEX IF NOT EXISTS idx_case_country_risk_level ON risk_case(country, risk_level);

-- 注释
COMMENT ON TABLE risk_case IS '风险案件表';
COMMENT ON COLUMN risk_case.biz_transaction_id IS '业务交易ID';
COMMENT ON COLUMN risk_case.risk_features IS '风险特征快照（JSONB格式）';

-- ============================================================================
-- 3. ai_decision_record 表 - AI决策记录表
-- ============================================================================
CREATE TABLE IF NOT EXISTS ai_decision_record (
    id BIGSERIAL PRIMARY KEY,
    
    -- 关联
    case_id BIGINT NOT NULL,
    prompt_version VARCHAR(20) NOT NULL,
    
    -- AI 分析结果
    ai_decision VARCHAR(20),  -- APPROVE, REJECT, UNCERTAIN
    ai_confidence DECIMAL(5,2),
    ai_reasoning TEXT,
    
    -- 相似案例
    similar_cases JSONB,  -- [{"id": 123, "similarity": 0.95}, ...]
    
    -- 规则查询结果
    rule_query_result JSONB,
    
    -- 历史分析结果
    history_analysis JSONB,
    
    -- Override 标记
    override_flag BOOLEAN DEFAULT FALSE,
    override_reason TEXT,
    final_decision VARCHAR(20),
    
    -- 性能指标
    retrieval_time_ms INT,
    llm_call_time_ms INT,
    total_time_ms INT,
    
    -- 系统字段
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    version INT NOT NULL DEFAULT 0,
    
    -- 外键
    CONSTRAINT fk_ai_case FOREIGN KEY (case_id) REFERENCES risk_case(id)
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_ai_case_id ON ai_decision_record(case_id);
CREATE INDEX IF NOT EXISTS idx_ai_prompt_version ON ai_decision_record(prompt_version);
CREATE INDEX IF NOT EXISTS idx_ai_override ON ai_decision_record(override_flag);
CREATE INDEX IF NOT EXISTS idx_ai_created_at ON ai_decision_record(created_at);

-- 注释
COMMENT ON TABLE ai_decision_record IS 'AI决策记录表';
COMMENT ON COLUMN ai_decision_record.similar_cases IS '相似案例列表（JSONB格式）';

-- ============================================================================
-- 4. prompt_template 表 - Prompt模板表
-- ============================================================================
CREATE TABLE IF NOT EXISTS prompt_template (
    id BIGSERIAL PRIMARY KEY,
    
    -- 版本管理
    version VARCHAR(20) NOT NULL UNIQUE,  -- v1, v2, v3
    
    -- Prompt 内容
    system_prompt TEXT NOT NULL,
    user_prompt_template TEXT NOT NULL,
    
    -- 版本信息
    description TEXT,
    is_active BOOLEAN DEFAULT FALSE,
    
    -- 性能指标
    avg_response_time_ms INT,
    override_rate DECIMAL(5,2),
    
    -- 系统字段
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    version_num INT NOT NULL DEFAULT 0
);

-- 索引
CREATE UNIQUE INDEX IF NOT EXISTS idx_prompt_version ON prompt_template(version);
CREATE INDEX IF NOT EXISTS idx_prompt_is_active ON prompt_template(is_active);
CREATE INDEX IF NOT EXISTS idx_prompt_created_at ON prompt_template(created_at);

-- 注释
COMMENT ON TABLE prompt_template IS 'Prompt模板表';
COMMENT ON COLUMN prompt_template.version IS 'Prompt版本号';

-- ============================================================================
-- 5. case_audit_log 表 - 案件审计日志表
-- ============================================================================
CREATE TABLE IF NOT EXISTS case_audit_log (
    id BIGSERIAL PRIMARY KEY,
    
    -- 关联
    case_id BIGINT NOT NULL,
    operator_id BIGINT,
    
    -- 操作
    operation VARCHAR(50) NOT NULL,  -- CREATE, ANALYZE, APPROVE, REJECT, OVERRIDE
    old_value JSONB,
    new_value JSONB,
    
    -- 时间
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- 外键
    CONSTRAINT fk_audit_case FOREIGN KEY (case_id) REFERENCES risk_case(id),
    CONSTRAINT fk_audit_operator FOREIGN KEY (operator_id) REFERENCES sys_user(id)
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_audit_case_id ON case_audit_log(case_id);
CREATE INDEX IF NOT EXISTS idx_audit_operator_id ON case_audit_log(operator_id);
CREATE INDEX IF NOT EXISTS idx_audit_created_at ON case_audit_log(created_at);
CREATE INDEX IF NOT EXISTS idx_audit_operation ON case_audit_log(operation);

-- 注释
COMMENT ON TABLE case_audit_log IS '案件审计日志表';

-- ============================================================================
-- 6. ai_prompt_log 表 - AI调用日志表
-- ============================================================================
CREATE TABLE IF NOT EXISTS ai_prompt_log (
    id BIGSERIAL PRIMARY KEY,
    
    -- 关联
    case_id BIGINT NOT NULL,
    ai_decision_id BIGINT,
    
    -- Prompt 信息
    prompt_version VARCHAR(20) NOT NULL,
    system_prompt TEXT,
    user_prompt TEXT,
    
    -- LLM 响应
    llm_response TEXT,
    llm_model VARCHAR(100),
    
    -- Token 统计
    input_tokens INT,
    output_tokens INT,
    total_tokens INT,
    
    -- 性能指标
    latency_ms INT,
    
    -- 系统字段
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- 外键
    CONSTRAINT fk_prompt_log_case FOREIGN KEY (case_id) REFERENCES risk_case(id),
    CONSTRAINT fk_prompt_log_ai FOREIGN KEY (ai_decision_id) REFERENCES ai_decision_record(id)
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_prompt_log_case_id ON ai_prompt_log(case_id);
CREATE INDEX IF NOT EXISTS idx_prompt_log_ai_id ON ai_prompt_log(ai_decision_id);
CREATE INDEX IF NOT EXISTS idx_prompt_log_created_at ON ai_prompt_log(created_at);

-- 注释
COMMENT ON TABLE ai_prompt_log IS 'AI调用日志表';

-- ============================================================================
-- 7. ai_call_metrics 表 - AI调用性能指标表
-- ============================================================================
CREATE TABLE IF NOT EXISTS ai_call_metrics (
    id BIGSERIAL PRIMARY KEY,
    
    -- 调用信息
    case_id BIGINT,
    prompt_version VARCHAR(50),
    
    -- 性能指标
    total_latency_ms INT,
    rag_latency_ms INT,
    llm_latency_ms INT,
    
    -- Token 统计
    input_tokens INT,
    output_tokens INT,
    total_tokens INT,
    
    -- 成本估算
    estimated_cost DECIMAL(10,6),
    
    -- 状态
    status VARCHAR(20),  -- SUCCESS, TIMEOUT, ERROR
    error_message TEXT,
    
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- 外键
    CONSTRAINT fk_metrics_case FOREIGN KEY (case_id) REFERENCES risk_case(id)
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_metrics_case_id ON ai_call_metrics(case_id);
CREATE INDEX IF NOT EXISTS idx_metrics_created_at ON ai_call_metrics(created_at);
CREATE INDEX IF NOT EXISTS idx_metrics_status ON ai_call_metrics(status);

-- 注释
COMMENT ON TABLE ai_call_metrics IS 'AI调用性能指标表';

-- ============================================================================
-- 8. rag_retrieval_log 表 - RAG检索日志表
-- ============================================================================
CREATE TABLE IF NOT EXISTS rag_retrieval_log (
    id BIGSERIAL PRIMARY KEY,
    
    -- 检索信息
    case_id BIGINT,
    query_text TEXT,
    
    -- 检索结果
    retrieved_doc_ids JSONB,  -- [1, 2, 3, 4, 5]
    similarity_scores JSONB,  -- [0.92, 0.88, 0.85, 0.82, 0.79]
    
    -- 质量评估
    top_1_relevant BOOLEAN,
    top_5_hit_rate DECIMAL(3,2),
    
    -- 性能
    latency_ms INT,
    
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- 外键
    CONSTRAINT fk_rag_case FOREIGN KEY (case_id) REFERENCES risk_case(id)
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_rag_case_id ON rag_retrieval_log(case_id);
CREATE INDEX IF NOT EXISTS idx_rag_created_at ON rag_retrieval_log(created_at);

-- 注释
COMMENT ON TABLE rag_retrieval_log IS 'RAG检索日志表';

-- ============================================================================
-- 9. knowledge_document 表 - 知识库文档表（用于向量存储）
-- ============================================================================
CREATE TABLE IF NOT EXISTS knowledge_document (
    id BIGSERIAL PRIMARY KEY,
    
    -- 文档信息
    doc_type VARCHAR(50),  -- case_history, rule_definition, etc.
    title VARCHAR(255),
    content TEXT,
    
    -- 向量 (使用 BYTEA 存储，pgvector 可选)
    embedding BYTEA,
    
    -- 元数据
    metadata JSONB,
    
    -- 系统字段
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_knowledge_doc_type ON knowledge_document(doc_type);

-- 注释
COMMENT ON TABLE knowledge_document IS '知识库文档表（用于向量存储）';

-- ============================================================================
-- 10. 创建更新时间戳触发器函数
-- ============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 为所有需要的表创建触发器
CREATE TRIGGER update_sys_user_updated_at
BEFORE UPDATE ON sys_user
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_risk_case_updated_at
BEFORE UPDATE ON risk_case
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ai_decision_record_updated_at
BEFORE UPDATE ON ai_decision_record
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_prompt_template_updated_at
BEFORE UPDATE ON prompt_template
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_knowledge_document_updated_at
BEFORE UPDATE ON knowledge_document
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- 11. 初始化数据
-- ============================================================================

-- 插入默认用户
INSERT INTO sys_user (username, email, password_hash, full_name, role, status)
VALUES 
    ('admin', 'admin@example.com', '$2a$10$mki27e48XpR8ALAr125quuBaQerDzF82xHeJK7srY76wZHuncfMIi', 'Administrator', 'ADMIN', 'ACTIVE'),
    ('reviewer1', 'reviewer1@example.com', '$2a$10$mki27e48XpR8ALAr125quuBaQerDzF82xHeJK7srY76wZHuncfMIi', 'Reviewer 1', 'REVIEWER', 'ACTIVE'),
    ('analyst1', 'analyst1@example.com', '$2a$10$mki27e48XpR8ALAr125quuBaQerDzF82xHeJK7srY76wZHuncfMIi', 'Analyst 1', 'ANALYST', 'ACTIVE')
ON CONFLICT (username) DO NOTHING;

-- 插入初始 Prompt 版本
INSERT INTO prompt_template (version, system_prompt, user_prompt_template, description, is_active)
VALUES 
    ('v1', 
     'You are a risk analysis expert specializing in financial fraud detection. Your task is to analyze transaction cases and provide risk assessments.',
     'Analyze the following transaction case and provide a risk assessment:\n\nTransaction Details:\n{transaction_details}\n\nSimilar Historical Cases:\n{similar_cases}\n\nProvide your analysis in JSON format with: risk_level, confidence_score, key_risk_points, suggested_action.',
     'Initial version - Basic risk analysis',
     TRUE),
    ('v2',
     'You are an advanced risk analysis expert with deep knowledge of fraud patterns and regulatory requirements. Provide comprehensive risk assessments.',
     'Analyze the following transaction case with enhanced risk dimensions:\n\nTransaction Details:\n{transaction_details}\n\nSimilar Historical Cases:\n{similar_cases}\n\nRule Engine Results:\n{rule_results}\n\nProvide detailed analysis in JSON format.',
     'Enhanced version - Improved accuracy',
     FALSE)
ON CONFLICT (version) DO NOTHING;

-- ============================================================================
-- 12. 创建视图
-- ============================================================================

-- 案件摘要视图
CREATE OR REPLACE VIEW v_case_summary AS
SELECT 
    c.id,
    c.biz_transaction_id,
    c.amount,
    c.currency,
    c.country,
    c.risk_level,
    c.risk_status,
    u.username as reviewer_name,
    c.created_at,
    c.updated_at
FROM risk_case c
LEFT JOIN sys_user u ON c.reviewer_id = u.id
WHERE c.deleted_at IS NULL;

-- AI决策摘要视图
CREATE OR REPLACE VIEW v_ai_decision_summary AS
SELECT 
    a.id,
    a.case_id,
    a.prompt_version,
    a.ai_decision,
    a.ai_confidence,
    a.override_flag,
    a.final_decision,
    a.total_time_ms,
    a.created_at
FROM ai_decision_record a
WHERE a.deleted_at IS NULL;

-- ============================================================================
-- 13. 授予权限
-- ============================================================================

-- 授予 risk_control_user 用户所有权限
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO risk_control_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO risk_control_user;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO risk_control_user;

-- 提交事务
COMMIT;
