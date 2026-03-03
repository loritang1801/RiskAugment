from flask import Blueprint, request, jsonify
import logging

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)


@api_bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'risk-control-ai-service'
    }), 200


@api_bp.route('/version', methods=['GET'])
def version():
    """Get API version"""
    return jsonify({
        'version': '1.0.0',
        'service': 'risk-control-ai-service'
    }), 200
