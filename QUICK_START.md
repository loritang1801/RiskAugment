# Quick Start (Interview Demo)

This project can run without real upstream systems.

## 1. One-click startup (recommended on Windows)

Run in `risk-control-platform/`:

```powershell
.\start-simple.ps1
```

This starts:
- docker-compose infrastructure
- Java backend
- Python ai-service
- frontend dev server

If you prefer manual startup, use the steps below.

## 2. Start infrastructure (manual)

Run in `risk-control-platform/`:

```bash
docker-compose up -d
```

This provides:
- PostgreSQL (application data path): `localhost:5433`
- Redis: `localhost:6379`

Note:
- `5433` is the unified DB port used by backend + ai-service in this project.

## 3. Configure environment

Copy example file:

```bash
cp .env.example .env
```

Key interview settings:
- `AI_DECISION_MODE=llm_only`
- `AGENT_TOOL_ALLOW_FALLBACK=false`
- leave `RULE_ENGINE_URL` and `TRANSACTION_HISTORY_URL` empty

To keep backend and ai-service on the same DB in demo, use:
- `DATABASE_URL=postgresql://risk_control_user:risk_control_password@localhost:5433/risk_control_db`

## 4. Start backend

Run in `risk-control-platform/`:

```bash
mvn clean install
mvn spring-boot:run
```

Backend URL: `http://localhost:8080`

## 5. Start ai-service

Run in `risk-control-platform/ai-service/`:

```bash
pip install -r requirements.txt
python app.py
```

AI service URL: `http://localhost:5000`

## 6. Start frontend

Run in `risk-control-platform/frontend/`:

```bash
npm install
npm run dev
```

Frontend URL: `http://localhost:3000` (or Vite default output)

## 7. Verify

- Backend Swagger: `http://localhost:8080/swagger-ui.html`
- AI health: `http://localhost:5000/health`
- Frontend login:
  - username: `admin`
  - password: `admin123`
  - other default users: `reviewer1` / `analyst1` (same password `admin123`)
