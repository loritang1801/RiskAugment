#!/usr/bin/env python3
"""
Generate mixed real-like offline evaluation dataset (JSONL).
This dataset is intentionally not a simple score bucket mapping.
"""

import argparse
import json
import random
from pathlib import Path
from typing import Dict, List


LOW_COUNTRIES = ["US", "CA", "DE", "FR", "JP", "SG", "GB", "AU", "NL"]
MID_COUNTRIES = ["BR", "MX", "TR", "ID", "MY", "TH", "PH", "VN", "IN"]
HIGH_COUNTRIES = ["NG", "PK", "IR", "SY", "RU", "UA", "IQ", "SD"]

RULE_POOL = [
    "RULE_VELOCITY",
    "RULE_GEO_DISTANCE",
    "RULE_HIGH_AMOUNT",
    "RULE_HIGH_RISK_COUNTRY",
    "RULE_NEW_DEVICE",
    "RULE_DEVICE_FINGERPRINT",
    "RULE_SANCTION_SCREEN",
    "RULE_BEHAVIOR_SHIFT",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate mixed evaluation dataset")
    parser.add_argument("--output", required=True, help="Output JSONL path")
    parser.add_argument("--count", type=int, default=80, help="Number of samples")
    parser.add_argument("--seed", type=int, default=20260302, help="Random seed")
    return parser.parse_args()


def pick_country() -> str:
    r = random.random()
    if r < 0.52:
        return random.choice(LOW_COUNTRIES)
    if r < 0.85:
        return random.choice(MID_COUNTRIES)
    return random.choice(HIGH_COUNTRIES)


def score_country(country: str) -> int:
    if country in HIGH_COUNTRIES:
        return 2
    if country in MID_COUNTRIES:
        return 1
    return 0


def build_case(idx: int) -> Dict:
    amount = round(random.uniform(30, 55000), 2)
    country = pick_country()
    device_risk = random.choices(["LOW", "MEDIUM", "HIGH"], weights=[0.52, 0.33, 0.15], k=1)[0]
    user_label = random.choices(["trusted", "vip", "normal", "new_user"], weights=[0.26, 0.08, 0.46, 0.20], k=1)[0]
    rule_cnt = random.choices([0, 1, 2, 3], weights=[0.24, 0.42, 0.24, 0.10], k=1)[0]
    triggered_rules = random.sample(RULE_POOL, k=rule_cnt)

    risk_points = 0
    risk_points += score_country(country)
    if amount >= 25000:
        risk_points += 2
    elif amount >= 9000:
        risk_points += 1
    if device_risk == "HIGH":
        risk_points += 2
    elif device_risk == "MEDIUM":
        risk_points += 1
    if user_label == "new_user":
        risk_points += 1
    if rule_cnt >= 2:
        risk_points += 1
    if user_label in {"trusted", "vip"} and amount < 3000 and device_risk == "LOW":
        risk_points -= 2

    if risk_points >= 5:
        expected_risk_level = "HIGH"
        expected_action = "REJECT"
    elif risk_points >= 2:
        expected_risk_level = "MEDIUM"
        expected_action = "MANUAL_REVIEW"
    else:
        expected_risk_level = "LOW"
        expected_action = "APPROVE"

    # Add edge cases to avoid simple monotonic mapping.
    edge_tag = "none"
    if random.random() < 0.16:
        edge_tag = "edge_case"
        if expected_risk_level == "HIGH":
            expected_action = "MANUAL_REVIEW"
        elif expected_risk_level == "LOW" and amount > 12000:
            expected_risk_level = "MEDIUM"
            expected_action = "MANUAL_REVIEW"
        elif expected_risk_level == "MEDIUM" and user_label == "trusted" and device_risk == "LOW":
            expected_risk_level = "LOW"
            expected_action = "APPROVE"

    # Rule score is correlated but noisy.
    base_score = max(0.0, min(0.99, 0.14 + risk_points * 0.14 + random.uniform(-0.12, 0.12)))
    if edge_tag == "edge_case" and expected_risk_level == "LOW":
        base_score = min(base_score, 0.42)

    case_data = {
        "amount": amount,
        "currency": random.choice(["USD", "EUR", "GBP", "CNY"]),
        "country": country,
        "device_risk": device_risk,
        "user_label": user_label,
        "user_id": 300000 + idx,
        "rule_engine_score": round(base_score, 2),
        "triggered_rules": triggered_rules,
    }
    labels = {
        "expected_risk_level": expected_risk_level,
        "expected_action": expected_action,
        "min_confidence_score": 0.45 if expected_risk_level != "HIGH" else 0.5,
    }
    return {
        "case_id": f"eval-mixed-{idx:04d}",
        "case_data": case_data,
        "labels": labels,
        "metadata": {
            "source": "mixed_v2",
            "edge_tag": edge_tag,
            "risk_points": risk_points,
        },
    }


def main() -> int:
    args = parse_args()
    random.seed(args.seed)

    out = Path(args.output).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    rows: List[Dict] = [build_case(i + 1) for i in range(args.count)]
    with out.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"Generated {len(rows)} mixed samples -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
