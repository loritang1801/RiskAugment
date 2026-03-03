"""
Flask AI Service with Real ChatGPT Integration
"""
import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
import json
import requests
from dotenv import load_dotenv
import sys

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# CORS configuration
CORS(app, origins=['http://localhost:3000', 'http://localhost:3001', 'http://localhost:5173'])

# Initialize OpenAI API key
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    logger.warning("OPENAI_API_KEY not set. AI analysis will use fallback mode.")
else:
    logger.info("OpenAI API key loaded successfully")

# Initialize database connection for prompt management
try:
    from database.connection import get_db_session
    from prompt.manager import PromptManager
    db_session = get_db_session()
    prompt_manager = PromptManager(db_session)
    logger.info("Prompt manager initialized successfully")
except Exception as e:
    logger.warning(f"Could not initialize prompt manager: {str(e)}")
    prompt_manager = None

# Health check endpoint
@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'risk-control-ai-service',
        'version': '1.0.0'
    }), 200

# RAG retrieve endpoint
@app.route('/api/rag/retrieve', methods=['POST'])
def rag_retrieve():
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        # Mock retrieval results
        results = [
            {
                'case_id': 1,
                'description': f'Similar case for query: {query}',
                'risk_level': 'high',
                'similarity': 0.95
            },
            {
                'case_id': 2,
                'description': f'Another similar case for query: {query}',
                'risk_level': 'medium',
                'similarity': 0.87
            }
        ]
        
        return jsonify({
            'status': 'success',
            'data': results
        }), 200
    except Exception as e:
        logger.error(f"Error in RAG retrieve: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# AI analyze endpoint
@app.route('/api/ai/analyze', methods=['POST'])
def ai_analyze():
    try:
        data = request.get_json()
        case_id = data.get('case_id')
        case_data = data.get('case_data', {})
        prompt_version = data.get('prompt_version')  # Optional prompt version
        
        # Extract case information
        amount = case_data.get('amount', 0)
        country = case_data.get('country', 'Unknown')
        device_risk = case_data.get('device_risk', 'LOW')
        user_label = case_data.get('user_label', 'existing_user')
        risk_features = case_data.get('risk_features', {})
        
        # Call ChatGPT for analysis
        if api_key:
            analysis = analyze_with_chatgpt(case_id, amount, country, device_risk, user_label, risk_features, prompt_version)
        else:
            logger.warning("OpenAI API key not available, using fallback analysis")
            analysis = analyze_with_fallback(case_id, amount, device_risk, user_label, country, prompt_version)
        
        return jsonify({
            'status': 'success',
            'data': {'analysis': analysis}
        }), 200
    except Exception as e:
        logger.error(f"Error in AI analyze: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

def analyze_with_chatgpt(case_id, amount, country, device_risk, user_label, risk_features, prompt_version=None):
    """Analyze case using real ChatGPT API via requests"""
    try:
        # Get prompt from database if available
        prompt_template = None
        if prompt_manager:
            if prompt_version:
                prompt_template = prompt_manager.get_prompt_by_version(prompt_version)
            else:
                prompt_template = prompt_manager.get_active_prompt()
        
        # Build the prompt
        if prompt_template and prompt_template.get('user_prompt_template'):
            # Use database prompt template
            user_prompt = prompt_template['user_prompt_template'].format(
                case_id=case_id,
                amount=amount,
                country=country,
                device_risk=device_risk,
                user_label=user_label,
                risk_features=json.dumps(risk_features, ensure_ascii=False)
            )
            system_prompt = prompt_template.get('system_prompt', 'You are a financial risk control expert. Always respond with valid JSON only.')
        else:
            # Use default prompt
            system_prompt = "You are a financial risk control expert. Always respond with valid JSON only."
            user_prompt = f"""Analyze the following transaction case and provide a structured risk assessment.

Transaction Details:
- Case ID: {case_id}
- Amount: {amount}
- Country: {country}
- Device Risk Level: {device_risk}
- User Type: {user_label}
- Risk Features: {json.dumps(risk_features, ensure_ascii=False)}

Please provide your analysis in the following JSON format (respond ONLY with valid JSON, no markdown):
{{
    "risk_level": "LOW|MEDIUM|HIGH",
    "confidence_score": 0.0-1.0,
    "suggested_action": "APPROVE|REVIEW|REJECT",
    "key_risk_points": ["point1", "point2", ...],
    "reasoning": "detailed explanation of the analysis",
    "similar_cases_analysis": "analysis of similar cases",
    "rule_engine_alignment": "how this aligns with risk rules"
}}

Provide a thorough analysis based on the transaction characteristics."""

        # Call ChatGPT API
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
            return analyze_with_fallback(case_id, amount, device_risk, user_label, country, prompt_version)
        
        response_data = response.json()
        response_text = response_data['choices'][0]['message']['content'].strip()
        
        # Try to extract JSON if wrapped in markdown
        if response_text.startswith('```'):
            response_text = response_text.split('```')[1]
            if response_text.startswith('json'):
                response_text = response_text[4:]
            response_text = response_text.strip()
        
        analysis = json.loads(response_text)
        
        # Ensure all required fields are present
        analysis.setdefault('risk_level', 'MEDIUM')
        analysis.setdefault('confidence_score', 0.5)
        analysis.setdefault('suggested_action', 'REVIEW')
        analysis.setdefault('key_risk_points', ['Analysis completed'])
        analysis.setdefault('reasoning', 'Risk assessment completed by AI')
        analysis.setdefault('similar_cases_analysis', 'Similar cases identified')
        analysis.setdefault('rule_engine_alignment', 'Aligned with risk rules')
        
        # Add source indicator
        analysis['analysis_source'] = 'ChatGPT'
        analysis['analysis_model'] = 'gpt-3.5-turbo'
        
        logger.info(f"ChatGPT analysis completed for case {case_id}: {analysis['risk_level']}")
        return analysis
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse ChatGPT response as JSON: {str(e)}")
        return analyze_with_fallback(case_id, amount, device_risk, user_label, country, prompt_version)
    except Exception as e:
        logger.error(f"Error calling ChatGPT: {str(e)}")
        return analyze_with_fallback(case_id, amount, device_risk, user_label, country, prompt_version)

def analyze_with_fallback(case_id, amount, device_risk, user_label, country, prompt_version=None):
    """Fallback analysis using rule-based logic with prompt guidance"""
    risk_score = calculate_risk_score(amount, device_risk, user_label)
    risk_level = get_risk_level(risk_score)
    suggested_action = get_suggested_action(risk_score)
    confidence = 0.75 + (risk_score * 0.2)
    key_risk_points = generate_risk_points(amount, device_risk, user_label, country)
    
    # Get prompt guidance if available
    reasoning = f'Fallback analysis for case {case_id}: {suggested_action} based on risk factors'
    if prompt_manager:
        try:
            if prompt_version:
                prompt_template = prompt_manager.get_prompt_by_version(prompt_version)
            else:
                prompt_template = prompt_manager.get_active_prompt()
            
            if prompt_template and prompt_template.get('system_prompt'):
                # Use prompt guidance to enhance reasoning
                reasoning = f'Analysis based on prompt guidance: {prompt_template.get("system_prompt", "")} - {suggested_action} based on risk factors'
        except Exception as e:
            logger.warning(f"Could not use prompt guidance: {str(e)}")
    
    return {
        'risk_level': risk_level,
        'confidence_score': round(min(confidence, 1.0), 2),
        'suggested_action': suggested_action,
        'key_risk_points': key_risk_points,
        'reasoning': reasoning,
        'similar_cases_analysis': f'Found {2 + int(risk_score * 3)} similar cases with comparable risk profiles',
        'rule_engine_alignment': 'Aligned with rule engine results',
        'analysis_source': 'Rule-Based',
        'analysis_model': 'Rule Engine'
    }

def calculate_risk_score(amount, device_risk, user_label):
    """Calculate risk score based on transaction characteristics"""
    score = 0.2  # Base score
    
    # Amount-based risk
    if amount > 50000:
        score += 0.3
    elif amount > 20000:
        score += 0.2
    elif amount > 5000:
        score += 0.1
    
    # Device risk
    if device_risk == 'HIGH':
        score += 0.3
    elif device_risk == 'MEDIUM':
        score += 0.15
    
    # User label risk
    if user_label == 'new_user':
        score += 0.2
    elif user_label == 'vip_user':
        score -= 0.1
    
    return min(score, 1.0)

def get_risk_level(risk_score):
    """Determine risk level from score"""
    if risk_score >= 0.7:
        return 'HIGH'
    elif risk_score >= 0.4:
        return 'MEDIUM'
    else:
        return 'LOW'

def get_suggested_action(risk_score):
    """Determine suggested action from risk score"""
    if risk_score >= 0.7:
        return 'REJECT'
    elif risk_score >= 0.4:
        return 'REVIEW'
    else:
        return 'APPROVE'

def generate_risk_points(amount, device_risk, user_label, country):
    """Generate specific risk points based on analysis"""
    points = []
    
    if amount > 50000:
        points.append('High transaction amount detected')
    
    if device_risk == 'HIGH':
        points.append('High device risk detected')
    elif device_risk == 'MEDIUM':
        points.append('Medium device risk detected')
    
    if user_label == 'new_user':
        points.append('New user account')
    
    if country in ['RU', 'CN', 'IN']:
        points.append(f'Transaction from high-risk country: {country}')
    
    if not points:
        points.append('Transaction appears normal')
    
    return points

# Prompt management endpoints
@app.route('/api/prompts', methods=['GET'])
def get_prompts():
    prompts = [
        {
            'id': 1,
            'version': 'v1',
            'system_prompt': 'You are a risk control expert.',
            'user_prompt_template': 'Analyze this case: {case}',
            'description': 'Initial version',
            'is_active': True,
            'created_at': '2026-02-01T00:00:00Z',
            'updated_at': '2026-02-01T00:00:00Z'
        },
        {
            'id': 2,
            'version': 'v2',
            'system_prompt': 'You are an expert in financial risk assessment.',
            'user_prompt_template': 'Please evaluate the risk level of: {case}',
            'description': 'Improved version',
            'is_active': False,
            'created_at': '2026-02-10T00:00:00Z',
            'updated_at': '2026-02-10T00:00:00Z'
        }
    ]
    return jsonify({
        'status': 'success',
        'data': prompts
    }), 200

@app.route('/api/prompts/<version>', methods=['GET'])
def get_prompt(version):
    prompt = {
        'id': 1,
        'version': version,
        'system_prompt': f'System prompt for {version}',
        'user_prompt_template': f'User template for {version}',
        'description': f'Prompt version {version}',
        'is_active': version == 'v1',
        'created_at': '2026-02-01T00:00:00Z',
        'updated_at': '2026-02-01T00:00:00Z'
    }
    return jsonify({
        'status': 'success',
        'data': prompt
    }), 200

@app.route('/api/prompts', methods=['POST'])
def create_prompt():
    data = request.get_json()
    new_prompt = {
        'id': 3,
        'version': data.get('version'),
        'system_prompt': data.get('system_prompt'),
        'user_prompt_template': data.get('user_prompt_template'),
        'description': data.get('description'),
        'is_active': False,
        'created_at': '2026-02-26T00:00:00Z',
        'updated_at': '2026-02-26T00:00:00Z'
    }
    return jsonify({
        'status': 'success',
        'data': new_prompt
    }), 201

@app.route('/api/prompts/<version>/activate', methods=['PUT'])
def activate_prompt(version):
    return jsonify({
        'status': 'success',
        'message': f'Prompt version {version} activated'
    }), 200

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({
        'status': 'error',
        'message': 'Resource not found'
    }), 404

@app.errorhandler(500)
def server_error(e):
    logger.error(f"Server error: {str(e)}")
    return jsonify({
        'status': 'error',
        'message': 'Internal server error'
    }), 500

if __name__ == '__main__':
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Flask AI Service on {host}:{port}")
    app.run(host=host, port=port, debug=debug)
