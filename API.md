# API 文档

完整的 REST API 端点文档，包括请求/响应示例和错误码说明。

## 基础信息

- **基础 URL**: `http://localhost:8080/api`
- **认证**: Bearer Token (JWT)
- **内容类型**: `application/json`
- **字符编码**: UTF-8

## 错误响应格式

所有错误响应遵循统一格式：

```json
{
  "code": "ERROR_CODE",
  "message": "错误描述",
  "timestamp": "2024-02-26T10:30:00Z",
  "path": "/api/cases/123"
}
```

### 常见错误码

| 错误码 | HTTP 状态 | 说明 |
|--------|----------|------|
| INVALID_REQUEST | 400 | 请求参数无效 |
| UNAUTHORIZED | 401 | 未授权 |
| FORBIDDEN | 403 | 禁止访问 |
| NOT_FOUND | 404 | 资源不存在 |
| CONFLICT | 409 | 资源冲突 |
| INTERNAL_ERROR | 500 | 服务器内部错误 |
| SERVICE_UNAVAILABLE | 503 | 服务不可用 |

---

## 案件管理 API

### 获取案件列表

```
GET /cases
```

**查询参数**:
- `page` (int, optional): 页码，默认 1
- `pageSize` (int, optional): 每页数量，默认 20
- `status` (string, optional): 案件状态 (PENDING, APPROVED, REJECTED)
- `riskLevel` (string, optional): 风险等级 (LOW, MEDIUM, HIGH, CRITICAL)
- `country` (string, optional): 国家代码
- `transactionId` (string, optional): 交易 ID

**响应示例**:
```json
{
  "code": "SUCCESS",
  "data": {
    "total": 100,
    "page": 1,
    "pageSize": 20,
    "items": [
      {
        "id": "case_001",
        "transactionId": "txn_12345",
        "status": "PENDING",
        "riskLevel": "HIGH",
        "country": "CN",
        "amount": 50000.00,
        "description": "可疑交易",
        "createdAt": "2024-02-26T10:00:00Z",
        "updatedAt": "2024-02-26T10:00:00Z"
      }
    ]
  }
}
```

### 获取案件详情

```
GET /cases/{id}
```

**路径参数**:
- `id` (string, required): 案件 ID

**响应示例**:
```json
{
  "code": "SUCCESS",
  "data": {
    "id": "case_001",
    "transactionId": "txn_12345",
    "status": "PENDING",
    "riskLevel": "HIGH",
    "country": "CN",
    "amount": 50000.00,
    "description": "可疑交易",
    "createdAt": "2024-02-26T10:00:00Z",
    "updatedAt": "2024-02-26T10:00:00Z",
    "aiAnalysis": {
      "riskScore": 0.85,
      "decision": "REJECT",
      "reasoning": "交易金额异常，与历史交易不符",
      "similarCases": [
        {
          "id": "case_002",
          "similarity": 0.92,
          "decision": "REJECTED"
        }
      ]
    }
  }
}
```

### 创建案件

```
POST /cases
```

**请求体**:
```json
{
  "transactionId": "txn_12345",
  "country": "CN",
  "amount": 50000.00,
  "description": "可疑交易"
}
```

**响应示例**:
```json
{
  "code": "SUCCESS",
  "data": {
    "id": "case_001",
    "transactionId": "txn_12345",
    "status": "PENDING",
    "riskLevel": "MEDIUM",
    "country": "CN",
    "amount": 50000.00,
    "description": "可疑交易",
    "createdAt": "2024-02-26T10:00:00Z"
  }
}
```

### 更新案件

```
PUT /cases/{id}
```

**请求体**:
```json
{
  "status": "APPROVED",
  "riskLevel": "LOW",
  "description": "已审核，无风险"
}
```

**响应示例**:
```json
{
  "code": "SUCCESS",
  "data": {
    "id": "case_001",
    "status": "APPROVED",
    "riskLevel": "LOW",
    "updatedAt": "2024-02-26T10:30:00Z"
  }
}
```

### 删除案件

```
DELETE /cases/{id}
```

**响应示例**:
```json
{
  "code": "SUCCESS",
  "message": "案件已删除"
}
```

---

## AI 分析 API

### 执行 AI 分析

```
POST /ai/analyze
```

**请求体**:
```json
{
  "caseId": "case_001",
  "promptVersion": "v2"
}
```

**响应示例**:
```json
{
  "code": "SUCCESS",
  "data": {
    "recordId": "record_001",
    "caseId": "case_001",
    "promptVersion": "v2",
    "riskScore": 0.85,
    "decision": "REJECT",
    "reasoning": "交易金额异常，与历史交易不符",
    "similarCases": [
      {
        "id": "case_002",
        "similarity": 0.92,
        "decision": "REJECTED",
        "reason": "金额异常"
      }
    ],
    "executionTime": 3500,
    "tokensUsed": 1250,
    "createdAt": "2024-02-26T10:00:00Z"
  }
}
```

### 获取分析结果

```
GET /ai/decision/{recordId}
```

**响应示例**:
```json
{
  "code": "SUCCESS",
  "data": {
    "recordId": "record_001",
    "caseId": "case_001",
    "promptVersion": "v2",
    "riskScore": 0.85,
    "decision": "REJECT",
    "reasoning": "交易金额异常，与历史交易不符",
    "executionTime": 3500,
    "tokensUsed": 1250,
    "createdAt": "2024-02-26T10:00:00Z"
  }
}
```

---

## Prompt 管理 API

### 获取所有 Prompt 版本

```
GET /prompts
```

**响应示例**:
```json
{
  "code": "SUCCESS",
  "data": [
    {
      "version": "v1",
      "name": "基础版本",
      "description": "初始 Prompt 版本",
      "isActive": false,
      "content": "你是一个风险控制专家...",
      "createdAt": "2024-01-01T00:00:00Z",
      "updatedAt": "2024-01-01T00:00:00Z"
    },
    {
      "version": "v2",
      "name": "优化版本",
      "description": "改进的 Prompt 版本",
      "isActive": true,
      "content": "你是一个资深的风险控制专家...",
      "createdAt": "2024-02-01T00:00:00Z",
      "updatedAt": "2024-02-01T00:00:00Z"
    }
  ]
}
```

### 获取特定版本

```
GET /prompts/{version}
```

**响应示例**:
```json
{
  "code": "SUCCESS",
  "data": {
    "version": "v2",
    "name": "优化版本",
    "description": "改进的 Prompt 版本",
    "isActive": true,
    "content": "你是一个资深的风险控制专家...",
    "createdAt": "2024-02-01T00:00:00Z",
    "updatedAt": "2024-02-01T00:00:00Z"
  }
}
```

### 创建新版本

```
POST /prompts
```

**请求体**:
```json
{
  "version": "v3",
  "name": "增强版本",
  "description": "增强的 Prompt 版本",
  "content": "你是一个资深的风险控制专家..."
}
```

**响应示例**:
```json
{
  "code": "SUCCESS",
  "data": {
    "version": "v3",
    "name": "增强版本",
    "description": "增强的 Prompt 版本",
    "isActive": false,
    "content": "你是一个资深的风险控制专家...",
    "createdAt": "2024-02-26T10:00:00Z"
  }
}
```

### 激活版本

```
PUT /prompts/{version}/activate
```

**响应示例**:
```json
{
  "code": "SUCCESS",
  "data": {
    "version": "v3",
    "isActive": true,
    "activatedAt": "2024-02-26T10:00:00Z"
  }
}
```

---

## 审计日志 API

### 获取案件审计追溯

```
GET /cases/{caseId}/audit-trail
```

**响应示例**:
```json
{
  "code": "SUCCESS",
  "data": [
    {
      "id": "audit_001",
      "caseId": "case_001",
      "action": "CREATE",
      "operator": "user_001",
      "timestamp": "2024-02-26T10:00:00Z",
      "details": "创建案件"
    },
    {
      "id": "audit_002",
      "caseId": "case_001",
      "action": "ANALYZE",
      "operator": "system",
      "timestamp": "2024-02-26T10:05:00Z",
      "details": "执行 AI 分析，使用 Prompt v2"
    },
    {
      "id": "audit_003",
      "caseId": "case_001",
      "action": "APPROVE",
      "operator": "user_002",
      "timestamp": "2024-02-26T10:10:00Z",
      "details": "批准案件"
    }
  ]
}
```

### 获取执行链路

```
GET /cases/{caseId}/execution-chain
```

**响应示例**:
```json
{
  "code": "SUCCESS",
  "data": {
    "caseId": "case_001",
    "chain": [
      {
        "step": 1,
        "tool": "query_rule_engine",
        "status": "SUCCESS",
        "input": {"caseId": "case_001"},
        "output": {"ruleMatches": ["RULE_001", "RULE_002"]},
        "executionTime": 150
      },
      {
        "step": 2,
        "tool": "retrieve_similar_cases",
        "status": "SUCCESS",
        "input": {"caseId": "case_001", "topK": 5},
        "output": {"cases": [{"id": "case_002", "similarity": 0.92}]},
        "executionTime": 300
      },
      {
        "step": 3,
        "tool": "analyze_similar_cases",
        "status": "SUCCESS",
        "input": {"cases": [{"id": "case_002"}]},
        "output": {"analysis": "相似案例均被拒绝"},
        "executionTime": 200
      },
      {
        "step": 4,
        "tool": "query_transaction_history",
        "status": "SUCCESS",
        "input": {"transactionId": "txn_12345"},
        "output": {"history": [{"amount": 1000}, {"amount": 2000}]},
        "executionTime": 100
      },
      {
        "step": 5,
        "tool": "llm_call",
        "status": "SUCCESS",
        "input": {"prompt": "...", "context": "..."},
        "output": {"decision": "REJECT", "reasoning": "..."},
        "executionTime": 2500
      }
    ],
    "totalExecutionTime": 3250
  }
}
```

---

## 分析 API

### 审核时间统计

```
GET /analytics/review-efficiency
```

**查询参数**:
- `startDate` (string, optional): 开始日期 (YYYY-MM-DD)
- `endDate` (string, optional): 结束日期 (YYYY-MM-DD)
- `dimension` (string, optional): 统计维度 (DAILY, WEEKLY, MONTHLY)

**响应示例**:
```json
{
  "code": "SUCCESS",
  "data": {
    "averageReviewTime": 3500,
    "minReviewTime": 1200,
    "maxReviewTime": 8900,
    "totalCases": 150,
    "trend": [
      {
        "date": "2024-02-20",
        "averageTime": 3200,
        "caseCount": 20
      },
      {
        "date": "2024-02-21",
        "averageTime": 3600,
        "caseCount": 25
      }
    ]
  }
}
```

### Override 率统计

```
GET /analytics/override-rate
```

**查询参数**:
- `startDate` (string, optional): 开始日期
- `endDate` (string, optional): 结束日期
- `promptVersion` (string, optional): Prompt 版本

**响应示例**:
```json
{
  "code": "SUCCESS",
  "data": {
    "overallOverrideRate": 0.15,
    "byVersion": [
      {
        "version": "v1",
        "overrideRate": 0.20,
        "totalCases": 100,
        "overrideCases": 20
      },
      {
        "version": "v2",
        "overrideRate": 0.12,
        "totalCases": 150,
        "overrideCases": 18
      }
    ]
  }
}
```

### Prompt 版本对比

```
GET /analytics/prompt-comparison
```

**查询参数**:
- `versions` (string, required): 版本列表，逗号分隔 (v1,v2,v3)
- `startDate` (string, optional): 开始日期
- `endDate` (string, optional): 结束日期

**响应示例**:
```json
{
  "code": "SUCCESS",
  "data": {
    "comparison": [
      {
        "version": "v1",
        "totalCases": 100,
        "overrideRate": 0.20,
        "averageReviewTime": 3800,
        "accuracy": 0.80
      },
      {
        "version": "v2",
        "totalCases": 150,
        "overrideRate": 0.12,
        "averageReviewTime": 3500,
        "accuracy": 0.88
      }
    ]
  }
}
```

---

## 用户管理 API

### 获取用户列表

```
GET /users
```

**响应示例**:
```json
{
  "code": "SUCCESS",
  "data": [
    {
      "id": "user_001",
      "username": "admin",
      "email": "admin@example.com",
      "role": "ADMIN",
      "createdAt": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### 创建用户

```
POST /users
```

**请求体**:
```json
{
  "username": "reviewer",
  "email": "reviewer@example.com",
  "password": "password123",
  "role": "REVIEWER"
}
```

---

## 速率限制

- 标准限制: 100 请求/分钟
- 分析 API: 10 请求/分钟
- 认证端点: 5 请求/分钟

## 认证

所有 API 端点（除了登录）都需要在请求头中包含 JWT Token：

```
Authorization: Bearer <token>
```

## 版本控制

当前 API 版本: v1

未来版本将通过 URL 前缀区分：`/api/v2/...`

---

## Response Contract (Current)

All business endpoints return JSON with `status`:

```json
{
  "status": "success",
  "data": {},
  "message": "optional",
  "timestamp": "2026-02-28T15:00:00",
  "traceId": "uuid"
}
```

Error responses are normalized:

```json
{
  "status": "error",
  "code": "NOT_FOUND",
  "message": "Resource not found",
  "details": {},
  "path": "/api/xxx",
  "timestamp": "2026-02-28T15:00:00",
  "traceId": "uuid"
}
```

`X-Trace-Id` is always returned in response headers and matches `traceId` in body.
