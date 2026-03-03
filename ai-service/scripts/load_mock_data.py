#!/usr/bin/env python3
"""
Load mock data into the database.
"""

import json
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app
from src.database.connection import db
from src.database.models import RiskCase, PromptTemplate
from datetime import datetime


def load_mock_data_from_json(app, json_file: str):
    """Load mock data from JSON file."""
    
    with app.app_context():
        print(f"Loading mock data from {json_file}...")
        
        with open(json_file, 'r') as f:
            cases_data = json.load(f)
        
        print(f"Found {len(cases_data)} cases in JSON file")
        
        # Clear existing data
        print("Clearing existing risk cases...")
        RiskCase.query.delete()
        db.session.commit()
        
        # Insert new data
        print("Inserting mock data...")
        for i, case_data in enumerate(cases_data):
            try:
                case = RiskCase(
                    biz_transaction_id=case_data['biz_transaction_id'],
                    amount=case_data['amount'],
                    currency=case_data['currency'],
                    country=case_data.get('country'),
                    device_risk=case_data.get('device_risk'),
                    user_label=case_data.get('user_label'),
                    risk_features=case_data.get('risk_features', {}),
                    rule_engine_score=case_data.get('rule_engine_score'),
                    triggered_rules=case_data.get('triggered_rules', []),
                    risk_score=case_data.get('risk_score'),
                    risk_level=case_data.get('risk_level'),
                    risk_status=case_data.get('risk_status', 'PENDING'),
                    created_at=datetime.fromisoformat(case_data['created_at']) if 'created_at' in case_data else datetime.utcnow()
                )
                db.session.add(case)
                
                if (i + 1) % 100 == 0:
                    db.session.commit()
                    print(f"  Inserted {i + 1} cases...")
            except Exception as e:
                print(f"Error inserting case {i}: {str(e)}")
                db.session.rollback()
                continue
        
        # Final commit
        db.session.commit()
        print(f"✓ Successfully loaded {len(cases_data)} cases")


def initialize_prompt_templates(app):
    """Initialize default prompt templates."""
    
    with app.app_context():
        print("Initializing prompt templates...")
        
        # Check if templates already exist
        existing = PromptTemplate.query.count()
        if existing > 0:
            print(f"  Found {existing} existing templates, skipping initialization")
            return
        
        # Create default templates
        templates = [
            {
                'version': 'v1',
                'system_prompt': '''You are a risk analysis expert specializing in financial fraud detection. 
Your task is to analyze transaction cases and provide risk assessments based on the provided information.
Be concise and focus on key risk factors.''',
                'user_prompt_template': '''Analyze the following transaction case and provide a risk assessment:

Transaction Details:
- Amount: {amount} {currency}
- Country: {country}
- Device Risk: {device_risk}
- User Label: {user_label}
- Triggered Rules: {triggered_rules}

Similar Historical Cases:
{similar_cases}

Provide your analysis in JSON format with:
- risk_level: LOW, MEDIUM, or HIGH
- confidence_score: 0-1
- key_risk_points: list of main risk factors
- suggested_action: APPROVE or REJECT''',
                'description': 'Initial version - Basic risk analysis',
                'is_active': True
            },
            {
                'version': 'v2',
                'system_prompt': '''You are an advanced risk analysis expert with deep knowledge of fraud patterns and regulatory requirements.
Provide comprehensive risk assessments considering multiple dimensions.
Focus on both explicit rules and implicit risk patterns.''',
                'user_prompt_template': '''Analyze the following transaction case with enhanced risk dimensions:

Transaction Details:
- Amount: {amount} {currency}
- Country: {country}
- Device Risk: {device_risk}
- User Label: {user_label}
- Triggered Rules: {triggered_rules}

Rule Engine Results:
{rule_results}

Similar Historical Cases:
{similar_cases}

Provide detailed analysis in JSON format with:
- risk_level: LOW, MEDIUM, or HIGH
- confidence_score: 0-1
- key_risk_points: list of main risk factors
- pattern_analysis: analysis of fraud patterns
- suggested_action: APPROVE or REJECT
- reasoning: detailed explanation''',
                'description': 'Enhanced version - Improved accuracy with pattern analysis',
                'is_active': False
            }
        ]
        
        for template_data in templates:
            template = PromptTemplate(
                version=template_data['version'],
                system_prompt=template_data['system_prompt'],
                user_prompt_template=template_data['user_prompt_template'],
                description=template_data['description'],
                is_active=template_data['is_active']
            )
            db.session.add(template)
        
        db.session.commit()
        print(f"✓ Initialized {len(templates)} prompt templates")


def main():
    """Main function."""
    
    # Create app
    app = create_app('development')
    
    # Initialize prompt templates
    initialize_prompt_templates(app)
    
    # Load mock data if JSON file exists
    json_file = Path(__file__).parent / 'mock_data.json'
    if json_file.exists():
        load_mock_data_from_json(app, str(json_file))
    else:
        print(f"Mock data file not found: {json_file}")
        print("Run generate_mock_data.py first to generate mock data")
    
    print("\n✓ Data loading completed!")


if __name__ == '__main__':
    main()
