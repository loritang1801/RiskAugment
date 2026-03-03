# Upstream Integration Contract

This document defines the upstream APIs used by AI agent hybrid tools.

## 1. Rule Engine Integration

### Environment Variables

- `RULE_ENGINE_URL`: full URL for rule engine evaluation API.
- `RULE_ENGINE_TOKEN`: optional bearer token.
- `RULE_ENGINE_TIMEOUT_SECONDS`: request timeout (default `5`).

### Request

- Method: `POST`
- Content-Type: `application/json`
- Body:

```json
{
  "case_data": {
    "id": 123,
    "amount": 100000,
    "currency": "USD",
    "country": "US",
    "device_risk": "HIGH",
    "user_label": "new_user"
  }
}
```

### Response (recommended)

```json
{
  "status": "success",
  "data": {
    "risk_score": 82.3,
    "triggered_rules": ["RULE_HIGH_AMOUNT", "RULE_NEW_USER"],
    "rule_confidence": 0.91
  }
}
```

Also accepted:
- direct object without `status/data`
- aliases: `rule_score` or `score`, `rules`, `confidence`

## 2. Transaction History Integration

### Environment Variables

- `TRANSACTION_HISTORY_URL`: full URL for history query API.
- `TRANSACTION_HISTORY_TOKEN`: optional bearer token.
- `TRANSACTION_HISTORY_TIMEOUT_SECONDS`: request timeout (default `5`).

### Request

- Method: `POST`
- Content-Type: `application/json`
- Body:

```json
{
  "user_id": 456,
  "limit": 10
}
```

### Response (recommended)

```json
{
  "status": "success",
  "data": {
    "transactions": [
      { "id": 1, "amount": 100.0, "currency": "USD", "country": "US", "status": "APPROVED" },
      { "id": 2, "amount": 500.0, "currency": "USD", "country": "US", "status": "REJECTED" }
    ],
    "average_amount": 300.0,
    "approval_rate": 0.5
  }
}
```

If `average_amount` or `approval_rate` is missing, ai-service computes them from `transactions`.

## 3. Fallback Policy

- `AGENT_TOOL_ALLOW_FALLBACK=true`: tool failures degrade to safe fallback result.
- `AGENT_TOOL_ALLOW_FALLBACK=false` (default): tool returns error status.

Recommended:
- test/dev: `true`
- staging/prod: `false` unless explicit degraded-mode policy is approved
