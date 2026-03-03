# Documentation Guide

This file is the single entry point for project documentation.

## Read Order (Recommended)

1. `README.md`
2. `QUICK_START.md`
3. `DEPLOYMENT.md`
4. `API.md`
5. `DATABASE.md`
6. `DEVELOPMENT.md`
7. `PROMPT.md`
8. `ai-service/UPSTREAM_INTEGRATION.md` (only for hybrid mode)
9. `docs/metrics/README.md` (offline evaluation and metric reports)
10. `docs/interview/ONE_PAGER.md` (interview delivery script)
11. `docs/interview/README.md` (interview docs index + talk tracks)

## Current Core Docs

- `README.md`: Project overview, architecture, key capabilities.
- `QUICK_START.md`: Minimal startup flow for local run.
- `API.md`: Backend API contract and examples.
- `DATABASE.md`: Data model and schema details.
- `DEVELOPMENT.md`: Dev workflow and coding guidelines.
- `DEPLOYMENT.md`: Unified deployment instructions (demo + integrated modes).
- `PROMPT.md`: Prompt strategy and evolution notes.
- `ai-service/UPSTREAM_INTEGRATION.md`: Upstream tool API contracts.
- `docs/metrics/README.md`: evaluation assets, sample schema, and report outputs.
- `docs/interview/ARCHITECTURE_DELTA.md`: architecture evolution before/after.
- `docs/interview/METRICS_TIMELINE.md`: measured timeline from report artifacts.
- `docs/interview/ONE_PAGER.md`: concise interview narration material.
- `docs/interview/README.md`: interview docs entry.
- `docs/interview/TALK_TRACK_CN_3MIN.md`: Chinese 3-minute talk track.
- `docs/interview/TALK_TRACK_CN_10MIN.md`: Chinese 10-minute talk track.
- `docs/interview/QA_BANK_CN_20.md`: Chinese top-20 follow-up Q&A.
- `docs/interview/DEFENSE_SCRIPT_CN.md`: risk/weakness defense script.

## Archived Docs

Historical status snapshots and one-time progress reports were moved to:

- `docs/archive/status-reports/`

These files are useful for traceability, but should not be treated as the current source of truth.

## Maintenance Rules

- Add new long-term docs to project root only if they are stable and reusable.
- Put milestone/progress/temporary reports under `docs/archive/status-reports/`.
- Keep this file updated whenever doc structure changes.
