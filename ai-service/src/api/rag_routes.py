"""
RAG API routes for retrieval operations.
"""

from flask import Blueprint, request, jsonify, current_app
import logging
from typing import Dict, Any
import time

logger = logging.getLogger(__name__)

rag_bp = Blueprint('rag', __name__, url_prefix='/api/rag')


@rag_bp.route('/retrieve', methods=['POST'])
def retrieve_similar_cases():
    """
    Retrieve similar cases for a given case.
    
    Request body:
    {
        "case_id": 123,
        "top_k": 5,
        "similarity_threshold": 0.7
    }
    
    Response:
    {
        "status": "success",
        "data": {
            "query_case_id": 123,
            "similar_cases": [
                {
                    "id": 456,
                    "similarity": 0.95,
                    "case_data": {...}
                }
            ]
        }
    }
    """
    try:
        data = request.get_json(silent=True) or {}
        case_id = data.get('case_id')
        top_k = int(data.get('top_k', 5))
        similarity_threshold = float(data.get('similarity_threshold', 0.7))
        
        if not case_id:
            return jsonify({
                'status': 'error',
                'message': 'case_id is required'
            }), 400

        retriever = current_app.config.get('retriever')
        if not retriever:
            return jsonify({
                'status': 'error',
                'message': 'Retriever not initialized'
            }), 503

        query_case = retriever.get_case_by_id(int(case_id))
        if not query_case:
            return jsonify({
                'status': 'error',
                'message': f'Case not found: {case_id}'
            }), 404

        start = time.time()
        similar_cases = retriever.retrieve_similar_cases(
            query_case=query_case,
            top_k=top_k,
            similarity_threshold=similarity_threshold
        )
        retrieval_time_ms = int((time.time() - start) * 1000)
        
        return jsonify({
            'status': 'success',
            'data': {
                'query_case_id': case_id,
                'similar_cases': similar_cases,
                'retrieval_time_ms': retrieval_time_ms
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Error retrieving similar cases: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@rag_bp.route('/search', methods=['POST'])
def search_cases():
    """
    Search cases by criteria.
    
    Request body:
    {
        "criteria": {
            "country": "US",
            "risk_level": "HIGH",
            "device_risk": "HIGH"
        },
        "limit": 10
    }
    
    Response:
    {
        "status": "success",
        "data": {
            "cases": [...],
            "total": 10
        }
    }
    """
    try:
        data = request.get_json(silent=True) or {}
        criteria = data.get('criteria', {})
        limit = int(data.get('limit', 10))

        retriever = current_app.config.get('retriever')
        if not retriever:
            return jsonify({
                'status': 'error',
                'message': 'Retriever not initialized'
            }), 503

        cases = retriever.retrieve_by_criteria(criteria, limit=limit)
        
        return jsonify({
            'status': 'success',
            'data': {
                'cases': cases,
                'total': len(cases)
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Error searching cases: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@rag_bp.route('/stats', methods=['GET'])
def get_rag_stats():
    """
    Get RAG statistics.
    
    Response:
    {
        "status": "success",
        "data": {
            "total_documents": 1000,
            "indexed_documents": 950,
            "avg_retrieval_time_ms": 150
        }
    }
    """
    try:
        from src.database.models import KnowledgeDocument, RiskCase
        from src.database.connection import db

        try:
            total_documents = db.session.query(KnowledgeDocument).count()
        except Exception:
            total_documents = 0

        try:
            total_cases = db.session.query(RiskCase).count()
        except Exception:
            total_cases = 0

        stats = {
            'total_documents': total_documents + total_cases,
            'indexed_documents': total_documents + total_cases,
            'avg_retrieval_time_ms': 0,
            'last_index_time': None
        }
        
        return jsonify({
            'status': 'success',
            'data': stats
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting RAG stats: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
