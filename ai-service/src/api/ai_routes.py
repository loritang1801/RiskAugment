"""
AI analysis API routes.
"""

from flask import Blueprint, request, jsonify, current_app
import logging
import os
import time
import uuid
from collections import deque, Counter
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from statistics import mean

logger = logging.getLogger(__name__)

ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')
ANALYZE_EVENTS = deque(maxlen=500)
ANALYZE_TIMEOUT_SECONDS = int(os.getenv('ANALYZE_TIMEOUT_SECONDS', '90'))


def _percentile(values, p):
    if not values:
        return 0
    if len(values) == 1:
        return values[0]
    values = sorted(values)
    rank = (len(values) - 1) * p
    lower = int(rank)
    upper = min(lower + 1, len(values) - 1)
    weight = rank - lower
    return values[lower] * (1 - weight) + values[upper] * weight


def _classify_error(message: str) -> str:
    text = (message or "").lower()
    if "rate limit" in text or "429" in text or "1302" in text:
        return "rate_limit"
    if "timeout" in text:
        return "timeout"
    if "connection" in text or "network" in text or "dns" in text:
        return "network"
    if "json" in text or "parse" in text:
        return "parse"
    return "other"


def _build_degraded_analysis(trace_id: str, error_message: str, case_data=None) -> dict:
    payload = case_data or {}
    score_raw = payload.get('rule_engine_score', payload.get('risk_score', 0))
    try:
        score = float(score_raw or 0)
    except (TypeError, ValueError):
        score = 0.0

    amount_raw = payload.get('amount', 0)
    try:
        amount = float(amount_raw or 0)
    except (TypeError, ValueError):
        amount = 0.0

    device_risk = str(payload.get('device_risk', '')).upper()
    currency = str(payload.get('currency', 'USD'))
    country = str(payload.get('country', 'UNKNOWN'))
    score_ratio = score / 100.0 if score > 1 else score
    score_ratio = max(0.0, min(1.0, score_ratio))

    if score_ratio >= 0.75 or (amount >= 15000 and device_risk == 'HIGH'):
        risk_level = 'HIGH'
        suggested_action = 'REJECT'
        confidence_score = 0.55
    elif score_ratio >= 0.35 or device_risk in {'MEDIUM', 'HIGH'}:
        risk_level = 'MEDIUM'
        suggested_action = 'MANUAL_REVIEW'
        confidence_score = 0.45
    else:
        risk_level = 'LOW'
        suggested_action = 'APPROVE'
        confidence_score = 0.40

    key_points = [
        f"规则评分 {score_ratio:.2f}，设备风险 {device_risk or 'UNKNOWN'}。",
        f"交易金额 {amount:.2f} {currency}，国家/地区 {country}。",
        f"因分析链路异常触发降级策略，当前建议动作为 {suggested_action}。"
    ]

    return {
        'risk_level': risk_level,
        'confidence_score': confidence_score,
        'key_risk_points': key_points,
        'suggested_action': suggested_action,
        'reasoning': (
            "模型分析链路出现异常，系统已启用保守降级策略。"
            f"当前基于规则评分 {score_ratio:.2f}、设备风险 {device_risk or 'UNKNOWN'}、"
            f"交易金额 {amount:.2f} {currency} 和地区 {country} 生成临时结论。"
            "请在业务侧结合完整上下文进行人工复核。"
        ),
        'similar_cases_analysis': '当前为降级分析结果，相似案例链路未返回稳定输出。',
        'similar_cases_details': [],
        'rule_engine_alignment': f"降级模式下采用基础规则信号。rule_score={score_ratio:.2f}。",
        'analysis_source': 'degraded_fallback',
        'analysis_model': 'fallback',
        'metadata': {
            'degraded': True,
            'trace_id': trace_id,
            'error_message': error_message,
            'total_time_ms': 0,
            'response_path': 'degraded_fallback'
        }
    }


@ai_bp.route('/analyze', methods=['POST'])
def analyze_case():
    """
    Analyze a risk case using AI Agent.
    
    Request body:
    {
        "case_id": 123,
        "case_data": {
            "amount": 100000,
            "currency": "USD",
            "country": "US",
            "device_risk": "HIGH",
            "user_label": "new_user",
            "user_id": 456
        },
        "prompt_version": "v1"
    }
    
    Response:
    {
        "status": "success",
        "data": {
            "case_id": 123,
            "analysis": {
                "risk_level": "HIGH",
                "confidence_score": 0.85,
                "key_risk_points": [...],
                "suggested_action": "REJECT",
                "metadata": {...}
            }
        }
    }
    """
    try:
        trace_id = request.headers.get('X-Trace-Id') or str(uuid.uuid4())
        data = request.get_json(silent=True) or {}
        case_id = data.get('case_id')
        case_data = data.get('case_data')
        prompt_version = data.get('prompt_version')
        
        if not case_id or not case_data:
            ANALYZE_EVENTS.append({
                "timestamp": int(time.time()),
                "trace_id": trace_id,
                "status": "failed",
                "latency_ms": 0,
                "error_category": "validation"
            })
            return jsonify({
                'status': 'error',
                'message': 'case_id and case_data are required'
            }), 400
        
        # Get agent from app context
        agent = current_app.config.get('ai_agent')
        if not agent:
            logger.error("AI Agent not initialized")
            ANALYZE_EVENTS.append({
                "timestamp": int(time.time()),
                "trace_id": trace_id,
                "status": "failed",
                "latency_ms": 0,
                "error_category": "service_unavailable"
            })
            return jsonify({
                'status': 'error',
                'message': 'AI service not available'
            }), 503
        
        # Analyze case with server-side timeout guard.
        start_time = time.time()
        app_obj = current_app._get_current_object()
        def _run_with_app_context():
            with app_obj.app_context():
                return agent.analyze_case(case_data, prompt_version)

        with ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(_run_with_app_context)
            try:
                analysis = future.result(timeout=max(1, ANALYZE_TIMEOUT_SECONDS))
            except FutureTimeoutError:
                future.cancel()
                raise RuntimeError(f"analyze timeout after {ANALYZE_TIMEOUT_SECONDS}s")
        total_time = int((time.time() - start_time) * 1000)
        
        # Add total time to metadata
        if 'metadata' not in analysis:
            analysis['metadata'] = {}
        analysis['metadata']['total_time_ms'] = total_time
        analysis['metadata']['trace_id'] = trace_id
        if 'response_path' not in analysis['metadata']:
            source = str(analysis.get('analysis_source') or '')
            if source == 'degraded_fallback':
                analysis['metadata']['response_path'] = 'degraded_fallback'
            elif source.startswith('llm:'):
                analysis['metadata']['response_path'] = 'llm_structured'
            else:
                analysis['metadata']['response_path'] = 'unknown'
        stage_time = (
            (analysis.get('execution_metrics') or {}).get('stage_time_ms')
            if isinstance(analysis, dict)
            else {}
        )
        ANALYZE_EVENTS.append({
            "timestamp": int(time.time()),
            "trace_id": trace_id,
            "status": "success",
            "latency_ms": total_time,
            "stage_time_ms": stage_time if isinstance(stage_time, dict) else {}
        })
        
        response = jsonify({
            'status': 'success',
            'data': {
                'case_id': case_id,
                'analysis': analysis
            }
        })
        response.headers['X-Trace-Id'] = trace_id
        return response, 200
    
    except Exception as e:
        logger.error(f"Error analyzing case: {str(e)}")
        trace_id = trace_id if 'trace_id' in locals() else str(uuid.uuid4())
        error_message = str(e)
        degraded_analysis = _build_degraded_analysis(trace_id, error_message, case_data=(data.get('case_data') if 'data' in locals() and isinstance(data, dict) else None))
        category = _classify_error(error_message)
        ANALYZE_EVENTS.append({
            "timestamp": int(time.time()),
            "trace_id": trace_id,
            "status": "degraded",
            "latency_ms": 0,
            "error_category": category
        })
        degraded_analysis['metadata']['error_category'] = category
        response = jsonify({
            'status': 'success',
            'message': 'analysis_degraded',
            'data': {
                'case_id': (data.get('case_id') if 'data' in locals() and isinstance(data, dict) else None),
                'analysis': degraded_analysis
            }
        })
        response.headers['X-Trace-Id'] = trace_id
        return response, 200


@ai_bp.route('/metrics/health', methods=['GET'])
def get_analyze_health_metrics():
    """
    Get lightweight analyze-chain health metrics from recent in-memory events.
    """
    try:
        limit = int(request.args.get('limit', 200))
        if limit <= 0:
            limit = 200
        events = list(ANALYZE_EVENTS)[-limit:]

        total = len(events)
        success_events = [e for e in events if e.get('status') == 'success']
        degraded_events = [e for e in events if e.get('status') == 'degraded']
        failed_events = [e for e in events if e.get('status') == 'failed']
        latencies = [int(e.get('latency_ms', 0)) for e in success_events if int(e.get('latency_ms', 0)) > 0]

        stage_keys = ['rule', 'retrieval', 'similar_analysis', 'transaction_history', 'llm', 'total']
        stage_avg = {}
        for key in stage_keys:
            values = []
            for event in success_events:
                stage_map = event.get('stage_time_ms') or {}
                if isinstance(stage_map, dict) and key in stage_map:
                    try:
                        values.append(float(stage_map[key]))
                    except (ValueError, TypeError):
                        continue
            stage_avg[key] = round(mean(values), 2) if values else 0

        error_categories = Counter(
            e.get('error_category', 'other') for e in failed_events
        )

        return jsonify({
            'status': 'success',
            'data': {
                'window_size': limit,
                'total_requests': total,
                'success_requests': len(success_events),
                'degraded_requests': len(degraded_events),
                'failed_requests': len(failed_events),
                'degraded_rate': round(len(degraded_events) / total, 4) if total else 0,
                'failure_rate': round(len(failed_events) / total, 4) if total else 0,
                'latency_ms': {
                    'avg': round(mean(latencies), 2) if latencies else 0,
                    'p50': round(_percentile(latencies, 0.5), 2) if latencies else 0,
                    'p95': round(_percentile(latencies, 0.95), 2) if latencies else 0,
                    'max': max(latencies) if latencies else 0
                },
                'stage_avg_ms': stage_avg,
                'error_categories': dict(error_categories)
            }
        }), 200
    except Exception as e:
        logger.error(f"Error getting health metrics: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@ai_bp.route('/batch-analyze', methods=['POST'])
def batch_analyze():
    """
    Analyze multiple cases.
    
    Request body:
    {
        "cases": [
            {
                "case_id": 123,
                "case_data": {...}
            }
        ],
        "prompt_version": "v1"
    }
    
    Response:
    {
        "status": "success",
        "data": {
            "results": [
                {
                    "case_id": 123,
                    "analysis": {...},
                    "status": "success"
                }
            ],
            "total": 1,
            "success": 1,
            "failed": 0
        }
    }
    """
    try:
        data = request.get_json(silent=True) or {}
        cases = data.get('cases', [])
        prompt_version = data.get('prompt_version')
        
        if not cases:
            return jsonify({
                'status': 'error',
                'message': 'cases is required'
            }), 400
        
        # Get agent from app context
        agent = current_app.config.get('ai_agent')
        if not agent:
            logger.error("AI Agent not initialized")
            return jsonify({
                'status': 'error',
                'message': 'AI service not available'
            }), 503
        
        # Analyze cases
        results = []
        for case in cases:
            try:
                case_id = case.get('case_id')
                case_data = case.get('case_data')
                
                analysis = agent.analyze_case(case_data, prompt_version)
                
                results.append({
                    'case_id': case_id,
                    'analysis': analysis,
                    'status': 'success'
                })
            except Exception as e:
                logger.error(f"Error analyzing case {case.get('case_id')}: {str(e)}")
                results.append({
                    'case_id': case.get('case_id'),
                    'error': str(e),
                    'status': 'error'
                })
        
        success_count = sum(1 for r in results if r['status'] == 'success')
        failed_count = len(results) - success_count
        
        return jsonify({
            'status': 'success',
            'data': {
                'results': results,
                'total': len(cases),
                'success': success_count,
                'failed': failed_count
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Error batch analyzing cases: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@ai_bp.route('/prompts', methods=['GET'])
def get_prompts():
    """
    Get all prompt templates.
    
    Response:
    {
        "status": "success",
        "data": {
            "prompts": [
                {
                    "version": "v1",
                    "description": "Initial version",
                    "is_active": true
                }
            ]
        }
    }
    """
    try:
        # Get prompt manager from app context
        prompt_manager = current_app.config.get('prompt_manager')
        if not prompt_manager:
            logger.error("Prompt manager not initialized")
            return jsonify({
                'status': 'error',
                'message': 'Prompt manager not available'
            }), 503
        
        prompts = prompt_manager.get_all_prompts()
        
        return jsonify({
            'status': 'success',
            'data': {
                'prompts': prompts
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting prompts: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@ai_bp.route('/prompts/<version>/activate', methods=['PUT'])
def activate_prompt(version):
    """
    Activate a prompt version.
    
    Response:
    {
        "status": "success",
        "data": {
            "version": "v1",
            "is_active": true
        }
    }
    """
    try:
        # Get prompt manager from app context
        prompt_manager = current_app.config.get('prompt_manager')
        if not prompt_manager:
            logger.error("Prompt manager not initialized")
            return jsonify({
                'status': 'error',
                'message': 'Prompt manager not available'
            }), 503
        
        success = prompt_manager.activate_prompt(version)
        
        if success:
            return jsonify({
                'status': 'success',
                'data': {
                    'version': version,
                    'is_active': True
                }
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': f'Prompt version not found: {version}'
            }), 404
    
    except Exception as e:
        logger.error(f"Error activating prompt: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@ai_bp.route('/prompts/<version>', methods=['GET'])
def get_prompt_by_version(version):
    """
    Get prompt template by version.
    
    Response:
    {
        "status": "success",
        "data": {
            "version": "v1",
            "system_prompt": "...",
            "user_prompt_template": "...",
            "description": "...",
            "is_active": true
        }
    }
    """
    try:
        prompt_manager = current_app.config.get('prompt_manager')
        if not prompt_manager:
            logger.error("Prompt manager not initialized")
            return jsonify({
                'status': 'error',
                'message': 'Prompt manager not available'
            }), 503
        
        prompt = prompt_manager.get_prompt_by_version(version)
        
        if prompt:
            return jsonify({
                'status': 'success',
                'data': prompt
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': f'Prompt version not found: {version}'
            }), 404
    
    except Exception as e:
        logger.error(f"Error getting prompt: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@ai_bp.route('/prompts', methods=['POST'])
def create_prompt():
    """
    Create a new prompt template.
    
    Request body:
    {
        "version": "v3",
        "system_prompt": "...",
        "user_prompt_template": "...",
        "description": "..."
    }
    
    Response:
    {
        "status": "success",
        "data": {
            "id": 3,
            "version": "v3",
            "description": "...",
            "is_active": false
        }
    }
    """
    try:
        data = request.get_json(silent=True) or {}
        version = data.get('version')
        system_prompt = data.get('system_prompt')
        user_prompt_template = data.get('user_prompt_template')
        description = data.get('description')
        
        if not version or not system_prompt or not user_prompt_template:
            return jsonify({
                'status': 'error',
                'message': 'version, system_prompt, and user_prompt_template are required'
            }), 400
        
        prompt_manager = current_app.config.get('prompt_manager')
        if not prompt_manager:
            logger.error("Prompt manager not initialized")
            return jsonify({
                'status': 'error',
                'message': 'Prompt manager not available'
            }), 503
        
        result = prompt_manager.create_prompt(
            version=version,
            system_prompt=system_prompt,
            user_prompt_template=user_prompt_template,
            description=description
        )
        
        if result:
            return jsonify({
                'status': 'success',
                'data': result
            }), 201
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to create prompt'
            }), 500
    
    except Exception as e:
        logger.error(f"Error creating prompt: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@ai_bp.route('/prompts/active', methods=['GET'])
def get_active_prompt():
    """
    Get the currently active prompt template.
    
    Response:
    {
        "status": "success",
        "data": {
            "version": "v1",
            "system_prompt": "...",
            "user_prompt_template": "...",
            "description": "..."
        }
    }
    """
    try:
        prompt_manager = current_app.config.get('prompt_manager')
        if not prompt_manager:
            logger.error("Prompt manager not initialized")
            return jsonify({
                'status': 'error',
                'message': 'Prompt manager not available'
            }), 503
        
        prompt = prompt_manager.get_active_prompt()
        
        if prompt:
            return jsonify({
                'status': 'success',
                'data': prompt
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'No active prompt template found'
            }), 404
    
    except Exception as e:
        logger.error(f"Error getting active prompt: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
