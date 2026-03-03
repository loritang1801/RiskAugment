#!/usr/bin/env python3
"""
Generate offline evaluation dataset (JSONL).
"""

import argparse
import json
import random
from pathlib import Path
from typing import Dict, List, Tuple


LOW_COUNTRIES = ["US", "CA", "DE", "FR", "JP", "SG", "GB"]
MEDIUM_COUNTRIES = ["BR", "MX", "TR", "ID", "MY", "TH", "PH"]
HIGH_COUNTRIES = ["NG", "PK", "IR", "SY", "RU", "UA", "IQ"]

LOW_RULES = [[], ["RULE_BEHAVIOR_SHIFT"], ["RULE_VELOCITY"]]
MEDIUM_RULES = [["RULE_VELOCITY"], ["RULE_GEO_DISTANCE"], ["RULE_BEHAVIOR_SHIFT", "RULE_VELOCITY"]]
HIGH_RULES = [
    ["RULE_HIGH_AMOUNT", "RULE_NEW_DEVICE"],
    ["RULE_HIGH_RISK_COUNTRY", "RULE_NEW_ACCOUNT"],
    ["RULE_SANCTION_SCREEN", "RULE_HIGH_RISK_COUNTRY"],
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate evaluation dataset")
    parser.add_argument(
        "--output",
        required=True,
        help="Output JSONL path",
    )
    parser.add_argument("--count", type=int, default=100, help="Number of samples")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    return parser.parse_args()


def risk_bucket(index: int, total: int) -> str:
    ratio = index / total
    if ratio < 0.40:
        return "LOW"
    if ratio < 0.75:
        return "MEDIUM"
    return "HIGH"


def build_case(bucket: str, idx: int) -> Tuple[Dict, Dict]:
    user_id = 200000 + idx
    if bucket == "LOW":
        amount = round(random.uniform(20, 900), 2)
        case_data = {
            "amount": amount,
            "currency": random.choice(["USD", "EUR", "GBP", "CNY"]),
            "country": random.choice(LOW_COUNTRIES),
            "device_risk": "LOW",
            "user_label": random.choice(["trusted", "vip", "normal"]),
            "user_id": user_id,
            "rule_engine_score": round(random.uniform(0.02, 0.25), 2),
            "triggered_rules": random.choice(LOW_RULES),
        }
        labels = {
            "expected_risk_level": "LOW",
            "expected_action": "APPROVE",
            "min_confidence_score": 0.45,
        }
        return case_data, labels

    if bucket == "MEDIUM":
        amount = round(random.uniform(1200, 9800), 2)
        case_data = {
            "amount": amount,
            "currency": random.choice(["USD", "EUR", "GBP"]),
            "country": random.choice(MEDIUM_COUNTRIES),
            "device_risk": random.choice(["LOW", "MEDIUM"]),
            "user_label": random.choice(["normal", "new_user"]),
            "user_id": user_id,
            "rule_engine_score": round(random.uniform(0.35, 0.65), 2),
            "triggered_rules": random.choice(MEDIUM_RULES),
        }
        labels = {
            "expected_risk_level": "MEDIUM",
            "expected_action": "MANUAL_REVIEW",
            "min_confidence_score": 0.5,
        }
        return case_data, labels

    amount = round(random.uniform(10000, 50000), 2)
    case_data = {
        "amount": amount,
        "currency": "USD",
        "country": random.choice(HIGH_COUNTRIES),
        "device_risk": "HIGH",
        "user_label": "new_user",
        "user_id": user_id,
        "rule_engine_score": round(random.uniform(0.78, 0.99), 2),
        "triggered_rules": random.choice(HIGH_RULES),
    }
    labels = {
        "expected_risk_level": "HIGH",
        "expected_action": "REJECT",
        "min_confidence_score": 0.55,
        "must_contain_risk_points": ["high", "rule"],
    }
    return case_data, labels


def main() -> int:
    args = parse_args()
    random.seed(args.seed)
    out_path = Path(args.output).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    rows: List[Dict] = []
    for i in range(args.count):
        bucket = risk_bucket(i, args.count)
        case_data, labels = build_case(bucket, i + 1)
        row = {
            "case_id": f"eval-auto-{i + 1:04d}",
            "case_data": case_data,
            "labels": labels,
            "metadata": {
                "segment": bucket.lower(),
                "source": "synthetic_v1",
            },
        }
        rows.append(row)

    with out_path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"Generated {len(rows)} samples -> {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
