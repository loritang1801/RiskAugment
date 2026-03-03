# Deployment Guide

This document is the single deployment reference.

## 1. Deployment Modes

### Interview Demo Mode (recommended)

Use this when you do not have real upstream systems.

- `AI_DECISION_MODE=llm_only`
- `AGENT_TOOL_ALLOW_FALLBACK=false`
- no `RULE_ENGINE_URL`
- no `TRANSACTION_HISTORY_URL`

### Integrated Mode (optional)

Use this when upstream systems are available.

- `AI_DECISION_MODE=hybrid`
- configure `RULE_ENGINE_URL` and `TRANSACTION_HISTORY_URL`
- optionally configure tokens and timeouts

See `ai-service/UPSTREAM_INTEGRATION.md` for API contract details.

## 2. Prerequisites

- Java 17+
- Maven 3.8+
- Python 3.10+
- Node.js 18+
- Docker + Docker Compose

## 3. Infrastructure Startup

Run in `risk-control-platform/`:

```bash
docker-compose up -d
```

Provided services:
- PostgreSQL (application data path): `localhost:5433`
- Redis: `localhost:6379`

Note:
- backend and ai-service should both point to `localhost:5433`.

Stop:

```bash
docker-compose down
```

## 4. Environment Configuration

Copy environment template:

```bash
cp .env.example .env
```

For consistent demo data path, keep backend and ai-service using the same DB:

```env
DATABASE_URL=postgresql://risk_control_user:risk_control_password@localhost:5433/risk_control_db
```

## 5. Start Application Services

### Backend

In `risk-control-platform/`:

```bash
mvn clean install
mvn spring-boot:run
```

### AI Service

In `risk-control-platform/ai-service/`:

```bash
pip install -r requirements.txt
python app.py
```

### Frontend

In `risk-control-platform/frontend/`:

```bash
npm install
npm run dev
```

## 6. Health Checks

- Backend: `http://localhost:8080/swagger-ui.html`
- AI service: `http://localhost:5000/health`
- Frontend: `http://localhost:3000` (or Vite output)

## 7. Troubleshooting

### Backend cannot connect DB

- confirm Docker is running
- confirm `localhost:5433` is available
- check `application-dev.yml` and `.env` consistency

### AI service has no model output

- set valid provider key in `.env`
- or enable mock output only for local debug:
  - `LLM_ALLOW_MOCK=true`

### Hybrid mode returns tool errors

- expected if upstream URLs are not configured
- use `llm_only` for interview demo
