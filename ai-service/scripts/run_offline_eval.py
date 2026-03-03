#!/usr/bin/env python3
"""
Offline evaluator for AI case analysis.

Usage:
  python scripts/run_offline_eval.py --input ../docs/metrics/sample_eval_cases.jsonl
"""

import argparse
import csv
import json
import math
import statistics
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests


VALID_RISK_LEVELS = {"LOW", "MEDIUM", "HIGH"}
VALID_ACTIONS = {"APPROVE", "REJECT", "MANUAL_REVIEW"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run offline evaluation for /api/ai/analyze")
    parser.add_argument("--input", required=True, help="JSONL dataset path")
    parser.add_argument(
        "--endpoint",
        default="http://127.0.0.1:5000/api/ai/analyze",
        help="AI analyze endpoint",
    )
    parser.add_argument(
        "--output-dir",
        default="../docs/metrics/reports",
        help="Directory for markdown/csv reports",
    )
    parser.add_argument("--prompt-version", default=None, help="Optional prompt version")
    parser.add_argument("--timeout", type=float, default=30.0, help="Request timeout seconds")
    parser.add_argument("--retries", type=int, default=1, help="Retry count for failed calls")
    parser.add_argument("--workers", type=int, default=1, help="Concurrent workers")
    parser.add_argument("--dry-run", action="store_true", help="Validate dataset only")
    return parser.parse_args()


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    samples: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for i, raw in enumerate(f, start=1):
            line = raw.strip()
            if not line:
                continue
            try:
                sample = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Line {i}: invalid JSON ({exc})") from exc
            samples.append(sample)
    return samples


def validate_sample(sample: Dict[str, Any], line_no: int) -> List[str]:
    errors: List[str] = []

    case_id = sample.get("case_id")
    if not isinstance(case_id, str) or not case_id.strip():
        errors.append(f"Line {line_no}: case_id must be non-empty string")

    case_data = sample.get("case_data")
    if not isinstance(case_data, dict):
        errors.append(f"Line {line_no}: case_data must be object")
    else:
        for key in ("amount", "currency", "country", "device_risk", "user_label", "user_id"):
            if key not in case_data:
                errors.append(f"Line {line_no}: case_data.{key} is required")

    labels = sample.get("labels")
    if not isinstance(labels, dict):
        errors.append(f"Line {line_no}: labels must be object")
    else:
        expected_risk_level = str(labels.get("expected_risk_level", "")).upper()
        if expected_risk_level not in VALID_RISK_LEVELS:
            errors.append(
                f"Line {line_no}: labels.expected_risk_level must be one of {sorted(VALID_RISK_LEVELS)}"
            )
        expected_action = str(labels.get("expected_action", "")).upper()
        if expected_action not in VALID_ACTIONS:
            errors.append(
                f"Line {line_no}: labels.expected_action must be one of {sorted(VALID_ACTIONS)}"
            )

        min_conf = labels.get("min_confidence_score")
        if min_conf is not None and not isinstance(min_conf, (float, int)):
            errors.append(f"Line {line_no}: labels.min_confidence_score must be number")
        if isinstance(min_conf, (float, int)) and (min_conf < 0 or min_conf > 1):
            errors.append(f"Line {line_no}: labels.min_confidence_score must be in [0,1]")

        must_points = labels.get("must_contain_risk_points")
        if must_points is not None:
            if not isinstance(must_points, list) or not all(isinstance(x, str) for x in must_points):
                errors.append(
                    f"Line {line_no}: labels.must_contain_risk_points must be string array if provided"
                )

    return errors


def normalize_enum(value: Any) -> str:
    return str(value or "").strip().upper().replace("-", "_").replace(" ", "_")


def extract_analysis(payload: Dict[str, Any]) -> Dict[str, Any]:
    data = payload.get("data", {})
    if isinstance(data, dict):
        analysis = data.get("analysis")
        if isinstance(analysis, dict):
            return analysis
        if "risk_level" in data and "suggested_action" in data:
            return data
    return {}


def compute_percent(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def percentile(values: List[float], p: float) -> float:
    if not values:
        return 0.0
    if len(values) == 1:
        return values[0]
    values_sorted = sorted(values)
    rank = (len(values_sorted) - 1) * p
    lower = math.floor(rank)
    upper = math.ceil(rank)
    if lower == upper:
        return values_sorted[lower]
    weight = rank - lower
    return values_sorted[lower] * (1 - weight) + values_sorted[upper] * weight


def evaluate_sample(
    sample: Dict[str, Any],
    endpoint: str,
    prompt_version: Optional[str],
    timeout: float,
    retries: int,
) -> Dict[str, Any]:
    case_id = sample["case_id"]
    labels = sample.get("labels", {})
    payload: Dict[str, Any] = {
        "case_id": case_id,
        "case_data": sample["case_data"],
    }
    if prompt_version:
        payload["prompt_version"] = prompt_version

    attempt = 0
    last_error = ""
    latency_ms: Optional[int] = None
    analysis: Dict[str, Any] = {}
    trace_id = str(uuid.uuid4())

    while attempt <= retries:
        attempt += 1
        start = time.perf_counter()
        try:
            resp = requests.post(
                endpoint,
                json=payload,
                timeout=timeout,
                headers={"X-Trace-Id": trace_id},
            )
            latency_ms = int((time.perf_counter() - start) * 1000)
            if resp.status_code >= 400:
                last_error = f"HTTP {resp.status_code}: {resp.text[:200]}"
                continue
            body = resp.json()
            if body.get("status") != "success":
                last_error = f"non-success status: {body.get('status')}"
                continue
            analysis = extract_analysis(body)
            if not analysis:
                last_error = "empty analysis payload"
                continue
            last_error = ""
            break
        except Exception as exc:  # pylint: disable=broad-except
            latency_ms = int((time.perf_counter() - start) * 1000)
            last_error = str(exc)

    success = not last_error
    predicted_risk = normalize_enum(analysis.get("risk_level")) if success else ""
    predicted_action = normalize_enum(analysis.get("suggested_action")) if success else ""
    expected_risk = normalize_enum(labels.get("expected_risk_level"))
    expected_action = normalize_enum(labels.get("expected_action"))

    risk_correct = int(success and predicted_risk == expected_risk)
    action_correct = int(success and predicted_action == expected_action)

    key_risk_points = analysis.get("key_risk_points", []) if success else []
    if not isinstance(key_risk_points, list):
        key_risk_points = [str(key_risk_points)]

    checks = [
        bool(str(analysis.get("reasoning", "")).strip()) if success else False,
        bool(str(analysis.get("similar_cases_analysis", "")).strip()) if success else False,
        bool(str(analysis.get("rule_engine_alignment", "")).strip()) if success else False,
        len(key_risk_points) > 0 if success else False,
    ]
    completeness_score = sum(1 for c in checks if c) / 4.0

    confidence_score = analysis.get("confidence_score", None) if success else None
    min_conf = labels.get("min_confidence_score", None)
    confidence_pass = None
    if success and isinstance(min_conf, (int, float)) and isinstance(confidence_score, (int, float)):
        confidence_pass = int(confidence_score >= min_conf)

    risk_points_coverage = None
    must_points = labels.get("must_contain_risk_points", None)
    if success and isinstance(must_points, list) and must_points:
        combined = " ".join(str(x).lower() for x in key_risk_points)
        covered = sum(1 for item in must_points if str(item).lower() in combined)
        risk_points_coverage = covered / len(must_points)

    return {
        "case_id": case_id,
        "trace_id": trace_id,
        "status": "success" if success else "failed",
        "error": last_error,
        "latency_ms": latency_ms if latency_ms is not None else 0,
        "expected_risk_level": expected_risk,
        "predicted_risk_level": predicted_risk,
        "risk_correct": risk_correct,
        "expected_action": expected_action,
        "predicted_action": predicted_action,
        "action_correct": action_correct,
        "confidence_score": confidence_score if isinstance(confidence_score, (int, float)) else "",
        "min_confidence_score": min_conf if isinstance(min_conf, (int, float)) else "",
        "confidence_pass": confidence_pass if confidence_pass is not None else "",
        "completeness_score": round(completeness_score, 4),
        "risk_points_count": len(key_risk_points),
        "risk_points_coverage": (
            round(risk_points_coverage, 4) if isinstance(risk_points_coverage, float) else ""
        ),
        "analysis_source": analysis.get("analysis_source", "") if success else "",
        "analysis_model": analysis.get("analysis_model", "") if success else "",
        "degraded": int(success and str(analysis.get("analysis_source", "")).lower() == "degraded_fallback"),
        "degraded_error_category": (
            ((analysis.get("metadata") or {}).get("error_category", ""))
            if success and str(analysis.get("analysis_source", "")).lower() == "degraded_fallback"
            else ""
        ),
        "degraded_error_message": (
            ((analysis.get("metadata") or {}).get("error_message", ""))
            if success and str(analysis.get("analysis_source", "")).lower() == "degraded_fallback"
            else ""
        ),
    }


def summarize(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = len(results)
    success_rows = [r for r in results if r["status"] == "success"]
    failed_rows = [r for r in results if r["status"] != "success"]
    latencies = [float(r["latency_ms"]) for r in success_rows]

    risk_scored = len(success_rows)
    action_scored = len(success_rows)
    risk_correct = sum(int(r["risk_correct"]) for r in success_rows)
    action_correct = sum(int(r["action_correct"]) for r in success_rows)

    completeness = [float(r["completeness_score"]) for r in success_rows]
    degraded_count = sum(int(r.get("degraded", 0)) for r in success_rows)

    conf_rows = [r for r in success_rows if r["confidence_pass"] != ""]
    conf_pass = sum(int(r["confidence_pass"]) for r in conf_rows)

    coverage_rows = [r for r in success_rows if r["risk_points_coverage"] != ""]
    coverage_values = [float(r["risk_points_coverage"]) for r in coverage_rows]

    return {
        "total": total,
        "success": len(success_rows),
        "failed": len(failed_rows),
        "degraded_count": degraded_count,
        "degraded_rate": compute_percent(degraded_count, len(success_rows)),
        "failure_rate": compute_percent(len(failed_rows), total),
        "risk_level_accuracy": compute_percent(risk_correct, risk_scored),
        "action_accuracy": compute_percent(action_correct, action_scored),
        "explanation_completeness": statistics.mean(completeness) if completeness else 0.0,
        "confidence_threshold_pass_rate": compute_percent(conf_pass, len(conf_rows)),
        "risk_points_coverage": statistics.mean(coverage_values) if coverage_values else 0.0,
        "latency_avg_ms": statistics.mean(latencies) if latencies else 0.0,
        "latency_p50_ms": percentile(latencies, 0.50),
        "latency_p95_ms": percentile(latencies, 0.95),
        "latency_max_ms": max(latencies) if latencies else 0.0,
        "failure_examples": [f"{r['case_id']}: {r['error']}" for r in failed_rows[:5]],
    }


def write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_summary(path: Path, summary: Dict[str, Any], endpoint: str, input_path: Path) -> None:
    lines = [
        "# Offline Evaluation Summary",
        "",
        f"- Generated at: `{datetime.now().isoformat(timespec='seconds')}`",
        f"- Endpoint: `{endpoint}`",
        f"- Input: `{input_path}`",
        "",
        "## Aggregate Metrics",
        "",
        f"- Total samples: **{summary['total']}**",
        f"- Success: **{summary['success']}**",
        f"- Failed: **{summary['failed']}**",
        f"- Degraded (within success): **{summary['degraded_count']}**",
        f"- Degraded rate (within success): **{summary['degraded_rate']:.2%}**",
        f"- Failure rate: **{summary['failure_rate']:.2%}**",
        f"- Risk level accuracy: **{summary['risk_level_accuracy']:.2%}**",
        f"- Action accuracy: **{summary['action_accuracy']:.2%}**",
        f"- Explanation completeness: **{summary['explanation_completeness']:.2%}**",
        f"- Confidence threshold pass rate: **{summary['confidence_threshold_pass_rate']:.2%}**",
        f"- Risk points coverage: **{summary['risk_points_coverage']:.2%}**",
        "",
        "## Latency",
        "",
        f"- Avg: **{summary['latency_avg_ms']:.1f} ms**",
        f"- P50: **{summary['latency_p50_ms']:.1f} ms**",
        f"- P95: **{summary['latency_p95_ms']:.1f} ms**",
        f"- Max: **{summary['latency_max_ms']:.1f} ms**",
        "",
    ]
    if summary["failure_examples"]:
        lines.extend(["## Failure Examples", ""])
        for item in summary["failure_examples"]:
            lines.append(f"- {item}")
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = parse_args()
    input_path = Path(args.input).resolve()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    if not input_path.exists():
        raise FileNotFoundError(f"Input dataset not found: {input_path}")

    samples = load_jsonl(input_path)
    if not samples:
        raise ValueError("Input dataset is empty")

    validation_errors: List[str] = []
    for idx, sample in enumerate(samples, start=1):
        validation_errors.extend(validate_sample(sample, idx))

    if validation_errors:
        print("Dataset validation failed:")
        for err in validation_errors:
            print(f"  - {err}")
        return 1

    print(f"Validation passed: {len(samples)} samples")
    if args.dry_run:
        print("Dry run mode enabled: no requests sent.")
        return 0

    rows: List[Dict[str, Any]] = []
    workers = max(1, args.workers)
    if workers == 1:
        for i, sample in enumerate(samples, start=1):
            row = evaluate_sample(
                sample=sample,
                endpoint=args.endpoint,
                prompt_version=args.prompt_version,
                timeout=args.timeout,
                retries=max(args.retries, 0),
            )
            rows.append(row)
            print(
                f"[{i}/{len(samples)}] {row['case_id']} -> {row['status']} "
                f"(risk={row['predicted_risk_level'] or '-'}, action={row['predicted_action'] or '-'})"
            )
    else:
        with ThreadPoolExecutor(max_workers=workers) as executor:
            future_to_index = {
                executor.submit(
                    evaluate_sample,
                    sample,
                    args.endpoint,
                    args.prompt_version,
                    args.timeout,
                    max(args.retries, 0),
                ): idx
                for idx, sample in enumerate(samples, start=1)
            }
            for future in as_completed(future_to_index):
                idx = future_to_index[future]
                row = future.result()
                rows.append(row)
                print(
                    f"[{idx}/{len(samples)}] {row['case_id']} -> {row['status']} "
                    f"(risk={row['predicted_risk_level'] or '-'}, action={row['predicted_action'] or '-'})"
                )
        rows.sort(key=lambda r: r["case_id"])

    summary = summarize(rows)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = output_dir / f"{ts}_details.csv"
    md_path = output_dir / f"{ts}_summary.md"
    write_csv(csv_path, rows)
    write_summary(md_path, summary, args.endpoint, input_path)

    print("")
    print(f"Details written: {csv_path}")
    print(f"Summary written: {md_path}")
    print(
        "Metrics: "
        f"risk_acc={summary['risk_level_accuracy']:.2%}, "
        f"action_acc={summary['action_accuracy']:.2%}, "
        f"failure={summary['failure_rate']:.2%}, "
        f"p95={summary['latency_p95_ms']:.1f}ms"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
