-- H2 Database Initialization Script for Risk Control Platform

-- ============================================================================
-- 1. sys_user 表 - 系统用户表
-- ============================================================================
CREATE TABLE IF NOT EXISTS sys_user (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role VARCHAR(20) NOT NULL,
    department VARCHAR(100),
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    last_login_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    version INT NOT NULL DEFAULT 0
);

-- ============================================================================
-- 2. risk_case 表 - 风险案件表
-- ============================================================================
CREATE TABLE IF NOT EXISTS risk_case (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    biz_transaction_id VARCHAR(64) NOT NULL UNIQUE,
    amount DECIMAL(18,2) NOT NULL,
    currency VARCHAR(10) NOT NULL,
    country VARCHAR(10),
    device_risk VARCHAR(20),
    user_label VARCHAR(50),
    risk_features CLOB,
    rule_engine_score DECIMAL(5,2),
    triggered_rules CLOB,
    risk_score DECIMAL(5,2),
    risk_level VARCHAR(20),
    risk_status VARCHAR(30) NOT NULL,
    ai_decision_id BIGINT,
    final_decision VARCHAR(20),
    reviewer_id BIGINT,
    user_id BIGINT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    version INT NOT NULL DEFAULT 0,
    CONSTRAINT fk_case_reviewer FOREIGN KEY (reviewer_id) REFERENCES sys_user(id)
);

-- ============================================================================
-- 3. ai_decision_record 表 - AI决策记录表
-- ============================================================================
CREATE TABLE IF NOT EXISTS ai_decision_record (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    case_id BIGINT NOT NULL,
    prompt_version VARCHAR(20) NOT NULL,
    suggested_action VARCHAR(20),
    ai_confidence DECIMAL(5,2),
    ai_reasoning TEXT,
    similar_cases CLOB,
    rule_query_result CLOB,
    history_analysis CLOB,
    override_flag BOOLEAN DEFAULT FALSE,
    override_reason TEXT,
    final_decision VARCHAR(20),
    retrieval_time_ms INT,
    llm_call_time_ms INT,
    total_time_ms INT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    version INT NOT NULL DEFAULT 0,
    CONSTRAINT fk_ai_case FOREIGN KEY (case_id) REFERENCES risk_case(id)
);

-- ============================================================================
-- 4. prompt_template 表 - Prompt模板表
-- ============================================================================
CREATE TABLE IF NOT EXISTS prompt_template (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    version VARCHAR(20) NOT NULL UNIQUE,
    system_prompt TEXT NOT NULL,
    user_prompt_template TEXT NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT FALSE,
    avg_response_time_ms INT,
    override_rate DECIMAL(5,2),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    version_num INT NOT NULL DEFAULT 0
);

-- ============================================================================
-- 5. case_audit_log 表 - 案件审计日志表
-- ============================================================================
CREATE TABLE IF NOT EXISTS case_audit_log (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    case_id BIGINT NOT NULL,
    operator_id BIGINT,
    operation VARCHAR(50) NOT NULL,
    old_value CLOB,
    new_value CLOB,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_audit_case FOREIGN KEY (case_id) REFERENCES risk_case(id),
    CONSTRAINT fk_audit_operator FOREIGN KEY (operator_id) REFERENCES sys_user(id)
);

-- ============================================================================
-- 6. ai_prompt_log 表 - AI调用日志表
-- ============================================================================
CREATE TABLE IF NOT EXISTS ai_prompt_log (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    case_id BIGINT NOT NULL,
    ai_decision_id BIGINT,
    prompt_version VARCHAR(20) NOT NULL,
    system_prompt TEXT,
    user_prompt TEXT,
    llm_response TEXT,
    llm_model VARCHAR(100),
    input_tokens INT,
    output_tokens INT,
    total_tokens INT,
    latency_ms INT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_prompt_log_case FOREIGN KEY (case_id) REFERENCES risk_case(id),
    CONSTRAINT fk_prompt_log_ai FOREIGN KEY (ai_decision_id) REFERENCES ai_decision_record(id)
);

-- ============================================================================
-- 7. ai_call_metrics 表 - AI调用性能指标表
-- ============================================================================
CREATE TABLE IF NOT EXISTS ai_call_metrics (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    case_id BIGINT,
    prompt_version VARCHAR(50),
    total_latency_ms INT,
    rag_latency_ms INT,
    llm_latency_ms INT,
    input_tokens INT,
    output_tokens INT,
    total_tokens INT,
    estimated_cost DECIMAL(10,6),
    status VARCHAR(20),
    error_message TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_metrics_case FOREIGN KEY (case_id) REFERENCES risk_case(id)
);

-- ============================================================================
-- 8. rag_retrieval_log 表 - RAG检索日志表
-- ============================================================================
CREATE TABLE IF NOT EXISTS rag_retrieval_log (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    case_id BIGINT,
    query_text TEXT,
    retrieved_doc_ids CLOB,
    similarity_scores CLOB,
    top_1_relevant BOOLEAN,
    top_5_hit_rate DECIMAL(3,2),
    latency_ms INT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_rag_case FOREIGN KEY (case_id) REFERENCES risk_case(id)
);

-- ============================================================================
-- 9. knowledge_document 表 - 知识库文档表
-- ============================================================================
CREATE TABLE IF NOT EXISTS knowledge_document (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    doc_type VARCHAR(50),
    title VARCHAR(255),
    content TEXT,
    embedding BLOB,
    metadata CLOB,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 10. 初始化数据
-- ============================================================================

-- 插入默认用户
INSERT INTO sys_user (username, email, password_hash, full_name, role, status)
VALUES 
    ('admin', 'admin@example.com', '$2a$10$mki27e48XpR8ALAr125quuBaQerDzF82xHeJK7srY76wZHuncfMIi', 'Administrator', 'ADMIN', 'ACTIVE'),
    ('reviewer1', 'reviewer1@example.com', '$2a$10$mki27e48XpR8ALAr125quuBaQerDzF82xHeJK7srY76wZHuncfMIi', 'Reviewer 1', 'REVIEWER', 'ACTIVE'),
    ('analyst1', 'analyst1@example.com', '$2a$10$mki27e48XpR8ALAr125quuBaQerDzF82xHeJK7srY76wZHuncfMIi', 'Analyst 1', 'ANALYST', 'ACTIVE');

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
     FALSE);

-- 插入模拟案件数据
INSERT INTO risk_case (biz_transaction_id, amount, currency, country, device_risk, user_label, risk_level, risk_status, risk_score, created_at)
VALUES 
    ('TXN001', 5000.00, 'USD', 'US', 'LOW', 'existing_user', 'LOW', 'PENDING', 0.25, CURRENT_TIMESTAMP),
    ('TXN002', 15000.00, 'USD', 'CN', 'MEDIUM', 'new_user', 'MEDIUM', 'ANALYZING', 0.55, CURRENT_TIMESTAMP),
    ('TXN003', 50000.00, 'USD', 'RU', 'HIGH', 'vip_user', 'HIGH', 'PENDING', 0.85, CURRENT_TIMESTAMP),
    ('TXN004', 3000.00, 'EUR', 'DE', 'LOW', 'existing_user', 'LOW', 'APPROVED', 0.15, CURRENT_TIMESTAMP),
    ('TXN005', 25000.00, 'GBP', 'GB', 'MEDIUM', 'new_user', 'MEDIUM', 'REJECTED', 0.65, CURRENT_TIMESTAMP),
    ('TXN006', 8000.00, 'USD', 'JP', 'LOW', 'existing_user', 'LOW', 'PENDING', 0.30, CURRENT_TIMESTAMP),
    ('TXN007', 45000.00, 'USD', 'IN', 'HIGH', 'new_user', 'HIGH', 'ANALYZING', 0.80, CURRENT_TIMESTAMP),
    ('TXN008', 12000.00, 'EUR', 'FR', 'MEDIUM', 'existing_user', 'MEDIUM', 'PENDING', 0.50, CURRENT_TIMESTAMP),
    ('TXN009', 60000.00, 'USD', 'BR', 'HIGH', 'vip_user', 'HIGH', 'PENDING', 0.90, CURRENT_TIMESTAMP),
    ('TXN010', 2000.00, 'USD', 'CA', 'LOW', 'new_user', 'LOW', 'APPROVED', 0.20, CURRENT_TIMESTAMP);

-- 插入 AI 决策记录
INSERT INTO ai_decision_record (case_id, prompt_version, suggested_action, ai_confidence, total_time_ms)
VALUES 
    (1, 'v1', 'APPROVE', 0.92, 1250),
    (2, 'v1', 'REVIEW', 0.78, 1450),
    (3, 'v1', 'REJECT', 0.88, 1380),
    (4, 'v1', 'APPROVE', 0.95, 1100),
    (5, 'v1', 'REJECT', 0.85, 1320),
    (6, 'v1', 'APPROVE', 0.90, 1200),
    (7, 'v1', 'REJECT', 0.82, 1400),
    (8, 'v1', 'REVIEW', 0.75, 1350),
    (9, 'v1', 'REJECT', 0.91, 1280),
    (10, 'v1', 'APPROVE', 0.93, 1150);

-- 插入审计日志
INSERT INTO case_audit_log (case_id, operator_id, operation, created_at)
VALUES 
    (1, 1, 'CREATE', CURRENT_TIMESTAMP),
    (2, 1, 'CREATE', CURRENT_TIMESTAMP),
    (3, 1, 'CREATE', CURRENT_TIMESTAMP),
    (4, 2, 'APPROVE', CURRENT_TIMESTAMP),
    (5, 2, 'REJECT', CURRENT_TIMESTAMP);
