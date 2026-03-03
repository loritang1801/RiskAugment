#!/usr/bin/env python3
"""
Mock data generation script for risk control platform.
Generates 1000 mock risk cases with realistic patterns.
"""

import json
import random
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Configuration
TOTAL_CASES = 1000
VIOLATION_RATE = 0.20  # 20% of cases violate rules
COUNTRIES = ['US', 'CN', 'GB', 'JP', 'DE', 'FR', 'IN', 'BR', 'RU', 'MX']
DEVICE_RISKS = ['LOW', 'MEDIUM', 'HIGH']
USER_LABELS = ['new_user', 'existing_user', 'vip_user', 'suspicious_user']
CURRENCIES = ['USD', 'CNY', 'GBP', 'JPY', 'EUR']
RISK_LEVELS = ['LOW', 'MEDIUM', 'HIGH']
RISK_STATUSES = ['PENDING', 'ANALYZING', 'APPROVED', 'REJECTED']

# Risk rules
RULES = {
    'RULE_001': {'name': 'High amount transfer', 'threshold': 100000},
    'RULE_002': {'name': 'New user large transfer', 'threshold': 50000},
    'RULE_003': {'name': 'High risk country', 'countries': ['RU', 'IR', 'KP']},
    'RULE_004': {'name': 'Suspicious device', 'device_risk': 'HIGH'},
    'RULE_005': {'name': 'Multiple transfers in short time', 'count': 5},
}


def generate_risk_features() -> Dict[str, Any]:
    """Generate realistic risk features for a transaction."""
    return {
        'ip_address': f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}",
        'device_id': f"device_{random.randint(100000, 999999)}",
        'user_agent': random.choice([
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
            'Mozilla/5.0 (X11; Linux x86_64)',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X)'
        ]),
        'login_time': (datetime.now() - timedelta(hours=random.randint(0, 24))).isoformat(),
        'transaction_time': datetime.now().isoformat(),
        'browser': random.choice(['Chrome', 'Firefox', 'Safari', 'Edge']),
        'os': random.choice(['Windows', 'macOS', 'Linux', 'iOS', 'Android']),
        'location': {
            'country': random.choice(COUNTRIES),
            'city': f"City_{random.randint(1, 100)}",
            'latitude': round(random.uniform(-90, 90), 4),
            'longitude': round(random.uniform(-180, 180), 4)
        }
    }


def check_triggered_rules(case_data: Dict[str, Any]) -> List[str]:
    """Check which rules are triggered by the case."""
    triggered = []
    
    # Rule 001: High amount transfer
    if case_data['amount'] > RULES['RULE_001']['threshold']:
        triggered.append('RULE_001')
    
    # Rule 002: New user large transfer
    if case_data['user_label'] == 'new_user' and case_data['amount'] > RULES['RULE_002']['threshold']:
        triggered.append('RULE_002')
    
    # Rule 003: High risk country
    if case_data['country'] in RULES['RULE_003']['countries']:
        triggered.append('RULE_003')
    
    # Rule 004: Suspicious device
    if case_data['device_risk'] == 'HIGH':
        triggered.append('RULE_004')
    
    return triggered


def calculate_risk_score(triggered_rules: List[str], device_risk: str) -> tuple:
    """Calculate risk score and level based on triggered rules."""
    base_score = len(triggered_rules) * 20
    
    # Add device risk score
    if device_risk == 'HIGH':
        base_score += 30
    elif device_risk == 'MEDIUM':
        base_score += 15
    
    # Normalize to 0-100
    risk_score = min(base_score, 100)
    
    # Determine risk level
    if risk_score >= 70:
        risk_level = 'HIGH'
    elif risk_score >= 40:
        risk_level = 'MEDIUM'
    else:
        risk_level = 'LOW'
    
    return risk_score, risk_level


def generate_case(case_id: int, is_violation: bool = False) -> Dict[str, Any]:
    """Generate a single mock risk case."""
    
    # Generate base data
    amount = random.uniform(100, 500000) if not is_violation else random.uniform(100000, 1000000)
    country = random.choice(COUNTRIES)
    device_risk = random.choice(DEVICE_RISKS)
    user_label = random.choice(USER_LABELS)
    
    # For violation cases, increase risk factors
    if is_violation:
        device_risk = random.choice(['MEDIUM', 'HIGH'])
        user_label = random.choice(['new_user', 'suspicious_user'])
        country = random.choice(COUNTRIES + ['RU', 'IR'])  # Include high-risk countries
    
    # Generate risk features
    risk_features = generate_risk_features()
    risk_features['country'] = country
    
    # Check triggered rules
    case_data = {
        'amount': amount,
        'country': country,
        'device_risk': device_risk,
        'user_label': user_label
    }
    triggered_rules = check_triggered_rules(case_data)
    
    # Calculate risk score
    risk_score, risk_level = calculate_risk_score(triggered_rules, device_risk)
    
    # Generate case
    case = {
        'id': case_id,
        'biz_transaction_id': f"TXN_{case_id:06d}_{random.randint(100000, 999999)}",
        'amount': round(amount, 2),
        'currency': random.choice(CURRENCIES),
        'country': country,
        'device_risk': device_risk,
        'user_label': user_label,
        'risk_features': risk_features,
        'rule_engine_score': round(risk_score, 2),
        'triggered_rules': triggered_rules,
        'risk_score': round(risk_score, 2),
        'risk_level': risk_level,
        'risk_status': random.choice(RISK_STATUSES),
        'created_at': (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat(),
        'is_violation': is_violation
    }
    
    return case


def generate_all_cases(total: int = TOTAL_CASES, violation_rate: float = VIOLATION_RATE) -> List[Dict[str, Any]]:
    """Generate all mock cases."""
    cases = []
    violation_count = int(total * violation_rate)
    
    print(f"Generating {total} mock cases...")
    print(f"  - Normal cases: {total - violation_count}")
    print(f"  - Violation cases: {violation_count}")
    
    # Generate normal cases
    for i in range(total - violation_count):
        case = generate_case(i + 1, is_violation=False)
        cases.append(case)
        if (i + 1) % 100 == 0:
            print(f"  Generated {i + 1} normal cases...")
    
    # Generate violation cases
    for i in range(violation_count):
        case = generate_case(total - violation_count + i + 1, is_violation=True)
        cases.append(case)
        if (i + 1) % 50 == 0:
            print(f"  Generated {i + 1} violation cases...")
    
    # Shuffle cases
    random.shuffle(cases)
    
    print(f"✓ Generated {len(cases)} cases successfully")
    return cases


def save_to_json(cases: List[Dict[str, Any]], filename: str = 'mock_data.json'):
    """Save cases to JSON file."""
    with open(filename, 'w') as f:
        json.dump(cases, f, indent=2)
    print(f"✓ Saved to {filename}")


def save_to_sql(cases: List[Dict[str, Any]], filename: str = 'mock_data.sql'):
    """Save cases as SQL INSERT statements."""
    with open(filename, 'w') as f:
        f.write("-- Mock data for risk_case table\n")
        f.write("-- Generated by generate_mock_data.py\n\n")
        
        for case in cases:
            risk_features_json = json.dumps(case['risk_features']).replace("'", "''")
            triggered_rules_json = json.dumps(case['triggered_rules']).replace("'", "''")
            
            sql = f"""INSERT INTO risk_case (
                biz_transaction_id, amount, currency, country, device_risk, user_label,
                risk_features, rule_engine_score, triggered_rules, risk_score, risk_level,
                risk_status, created_at
            ) VALUES (
                '{case['biz_transaction_id']}',
                {case['amount']},
                '{case['currency']}',
                '{case['country']}',
                '{case['device_risk']}',
                '{case['user_label']}',
                '{risk_features_json}'::jsonb,
                {case['rule_engine_score']},
                '{triggered_rules_json}'::jsonb,
                {case['risk_score']},
                '{case['risk_level']}',
                '{case['risk_status']}',
                '{case['created_at']}'
            );
"""
            f.write(sql)
    
    print(f"✓ Saved SQL to {filename}")


def print_statistics(cases: List[Dict[str, Any]]):
    """Print statistics about generated cases."""
    print("\n=== Statistics ===")
    
    # Risk level distribution
    risk_levels = {}
    for case in cases:
        level = case['risk_level']
        risk_levels[level] = risk_levels.get(level, 0) + 1
    
    print("\nRisk Level Distribution:")
    for level in ['LOW', 'MEDIUM', 'HIGH']:
        count = risk_levels.get(level, 0)
        percentage = (count / len(cases)) * 100
        print(f"  {level}: {count} ({percentage:.1f}%)")
    
    # Status distribution
    statuses = {}
    for case in cases:
        status = case['risk_status']
        statuses[status] = statuses.get(status, 0) + 1
    
    print("\nStatus Distribution:")
    for status in ['PENDING', 'ANALYZING', 'APPROVED', 'REJECTED']:
        count = statuses.get(status, 0)
        percentage = (count / len(cases)) * 100
        print(f"  {status}: {count} ({percentage:.1f}%)")
    
    # Country distribution
    countries = {}
    for case in cases:
        country = case['country']
        countries[country] = countries.get(country, 0) + 1
    
    print("\nTop 5 Countries:")
    sorted_countries = sorted(countries.items(), key=lambda x: x[1], reverse=True)[:5]
    for country, count in sorted_countries:
        percentage = (count / len(cases)) * 100
        print(f"  {country}: {count} ({percentage:.1f}%)")
    
    # Violation rate
    violations = sum(1 for case in cases if case['is_violation'])
    print(f"\nViolation Rate: {violations}/{len(cases)} ({(violations/len(cases))*100:.1f}%)")
    
    # Average amount
    avg_amount = sum(case['amount'] for case in cases) / len(cases)
    print(f"Average Amount: ${avg_amount:,.2f}")


if __name__ == '__main__':
    # Generate cases
    cases = generate_all_cases(TOTAL_CASES, VIOLATION_RATE)
    
    # Print statistics
    print_statistics(cases)
    
    # Save to files
    save_to_json(cases, 'mock_data.json')
    save_to_sql(cases, 'mock_data.sql')
    
    print("\n✓ Mock data generation completed!")
