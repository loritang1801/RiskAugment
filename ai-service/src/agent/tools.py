"""
Tool definitions for AI Agent.
"""

import logging
import os
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
import requests

logger = logging.getLogger(__name__)


class Tool(ABC):
    """Base class for agent tools."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool."""
        pass


class RetrieveSimilarCasesTool(Tool):
    """Tool to retrieve similar cases using RAG."""
    
    def __init__(self, retriever):
        super().__init__(
            name="retrieve_similar_cases",
            description="Retrieve similar historical cases based on current case features"
        )
        self.retriever = retriever
    
    def execute(self, case_data: Dict[str, Any], top_k: int = 5, **kwargs) -> Dict[str, Any]:
        """
        Retrieve similar cases.
        
        Args:
            case_data: Current case data
            top_k: Number of similar cases to retrieve
            
        Returns:
            Similar cases with similarity scores
        """
        try:
            similar_cases = self.retriever.retrieve_similar_cases(case_data, top_k=top_k)
            for case in similar_cases:
                case.setdefault('match_source', 'rag')

            # Fallback 1: relaxed threshold retrieval from local historical cases.
            if not similar_cases:
                relaxed = self.retriever.retrieve_similar_cases(
                    case_data,
                    top_k=top_k,
                    similarity_threshold=0.0
                )
                for case in relaxed:
                    case['match_source'] = 'relaxed_rag'
                similar_cases = relaxed

            # Fallback 2: criteria-based retrieval and heuristic ranking.
            if not similar_cases:
                criteria = {}
                if case_data.get('country'):
                    criteria['country'] = case_data.get('country')
                if case_data.get('device_risk'):
                    criteria['device_risk'] = case_data.get('device_risk')
                if case_data.get('user_label'):
                    criteria['user_label'] = case_data.get('user_label')

                candidates = self.retriever.retrieve_by_criteria(criteria, limit=max(top_k * 3, 15))
                ranked = sorted(
                    candidates,
                    key=lambda item: self._heuristic_similarity(case_data, item),
                    reverse=True
                )
                filtered = []
                query_case_id = case_data.get('id')
                for candidate in ranked:
                    if query_case_id is not None and str(candidate.get('id')) == str(query_case_id):
                        continue
                    similarity = self._heuristic_similarity(case_data, candidate)
                    filtered.append({
                        'id': candidate.get('id'),
                        'similarity': round(float(similarity), 4),
                        'case_data': candidate,
                        'match_source': 'criteria_fallback'
                    })
                    if len(filtered) >= top_k:
                        break
                similar_cases = filtered

            # Fallback 3: synthetic proxy cases for demo/interview mode.
            if not similar_cases:
                similar_cases = self._build_proxy_similar_cases(case_data, top_k=min(top_k, 3))
            
            return {
                'status': 'success',
                'data': {
                    'similar_cases': similar_cases,
                    'count': len(similar_cases)
                }
            }
        except Exception as e:
            logger.error(f"Error retrieving similar cases: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'data': {'similar_cases': [], 'count': 0}
            }

    def _heuristic_similarity(self, query_case: Dict[str, Any], candidate: Dict[str, Any]) -> float:
        score = 0.0

        if str(query_case.get('country', '')).upper() == str(candidate.get('country', '')).upper():
            score += 0.25

        if str(query_case.get('device_risk', '')).upper() == str(candidate.get('device_risk', '')).upper():
            score += 0.2

        if str(query_case.get('user_label', '')).upper() == str(candidate.get('user_label', '')).upper():
            score += 0.2

        query_level = str(query_case.get('risk_level', '')).upper()
        candidate_level = str(candidate.get('risk_level', '')).upper()
        if query_level and query_level == candidate_level:
            score += 0.2

        query_amount = self._to_float(query_case.get('amount'))
        candidate_amount = self._to_float(candidate.get('amount'))
        if query_amount is not None and candidate_amount is not None:
            denominator = max(query_amount, candidate_amount, 1.0)
            distance_ratio = abs(query_amount - candidate_amount) / denominator
            amount_score = max(0.0, 1.0 - min(distance_ratio, 1.0))
            score += 0.15 * amount_score

        return min(max(score, 0.0), 0.99)

    def _to_float(self, value: Any) -> Optional[float]:
        try:
            if value is None:
                return None
            return float(value)
        except (TypeError, ValueError):
            return None

    def _build_proxy_similar_cases(self, case_data: Dict[str, Any], top_k: int = 3) -> List[Dict[str, Any]]:
        amount = self._to_float(case_data.get('amount')) or 1000.0
        currency = str(case_data.get('currency') or 'USD')
        country = str(case_data.get('country') or 'US')
        device_risk = str(case_data.get('device_risk') or 'LOW')
        user_label = str(case_data.get('user_label') or 'unknown')
        risk_level = str(case_data.get('risk_level') or 'MEDIUM')
        risk_status = str(case_data.get('risk_status') or 'COMPLETED')

        decision_by_risk = {
            'LOW': 'APPROVE',
            'MEDIUM': 'REVIEW',
            'HIGH': 'REJECT'
        }
        base_decision = decision_by_risk.get(risk_level.upper(), 'REVIEW')

        multipliers = [0.88, 1.05, 1.22]
        similarity_scores = [0.86, 0.81, 0.76]
        decisions = [base_decision, base_decision, 'REJECT' if base_decision != 'REJECT' else 'REVIEW']

        proxies: List[Dict[str, Any]] = []
        for idx in range(min(top_k, len(multipliers))):
            proxy_id = f"proxy-{case_data.get('id', 'x')}-{idx + 1}"
            proxy_amount = round(amount * multipliers[idx], 2)
            proxies.append({
                'id': proxy_id,
                'similarity': similarity_scores[idx],
                'match_source': 'heuristic_proxy',
                'case_data': {
                    'id': proxy_id,
                    'biz_transaction_id': f"SIM-{proxy_id}",
                    'amount': proxy_amount,
                    'currency': currency,
                    'country': country,
                    'device_risk': device_risk,
                    'user_label': user_label,
                    'risk_level': risk_level,
                    'risk_status': risk_status,
                    'final_decision': decisions[idx]
                }
            })
        return proxies


class QueryRuleEngineTool(Tool):
    """Tool to query rule engine results."""
    
    def __init__(self):
        super().__init__(
            name="query_rule_engine",
            description="Query rule engine to get risk score and triggered rules"
        )
        self.rule_engine_url = os.getenv('RULE_ENGINE_URL', '').strip()
        self.rule_engine_token = os.getenv('RULE_ENGINE_TOKEN', '').strip()
        self.timeout_seconds = int(os.getenv('RULE_ENGINE_TIMEOUT_SECONDS', '5'))
        self.allow_fallback = os.getenv('AGENT_TOOL_ALLOW_FALLBACK', 'false').lower() == 'true'
    
    def execute(self, case_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Query rule engine.
        
        Args:
            case_data: Case data to analyze
            
        Returns:
            Rule engine results
        """
        try:
            if not self.rule_engine_url:
                message = "RULE_ENGINE_URL is not configured"
                if self.allow_fallback:
                    return self._fallback_result(case_data, message)
                return {
                    'status': 'error',
                    'error': message,
                    'data': {'risk_score': 0, 'triggered_rules': []}
                }

            headers = {'Content-Type': 'application/json'}
            if self.rule_engine_token:
                headers['Authorization'] = f'Bearer {self.rule_engine_token}'

            response = requests.post(
                self.rule_engine_url,
                json={'case_data': case_data},
                headers=headers,
                timeout=self.timeout_seconds
            )
            response.raise_for_status()
            payload = response.json()

            if isinstance(payload, dict) and payload.get('status') == 'error':
                raise RuntimeError(str(payload.get('message') or 'Rule engine returned error'))

            data = payload.get('data') if isinstance(payload, dict) and isinstance(payload.get('data'), dict) else payload
            normalized = self._normalize_response(data)
            
            return {
                'status': 'success',
                'data': normalized
            }
        except Exception as e:
            logger.error(f"Error querying rule engine: {str(e)}")
            if self.allow_fallback:
                return self._fallback_result(case_data, str(e))
            return {
                'status': 'error',
                'error': str(e),
                'data': {'risk_score': 0, 'triggered_rules': []}
            }

    def _normalize_response(self, data: Any) -> Dict[str, Any]:
        if not isinstance(data, dict):
            raise ValueError("Invalid rule engine response format")

        risk_score_raw = data.get('risk_score', data.get('rule_score', data.get('score', 0)))
        try:
            risk_score = float(risk_score_raw)
        except (TypeError, ValueError):
            risk_score = 0.0

        triggered_rules_raw = data.get('triggered_rules', data.get('rules', []))
        if isinstance(triggered_rules_raw, list):
            triggered_rules = [str(r) for r in triggered_rules_raw]
        elif isinstance(triggered_rules_raw, dict):
            triggered_rules = [str(k) for k in triggered_rules_raw.keys()]
        elif triggered_rules_raw is None:
            triggered_rules = []
        else:
            triggered_rules = [str(triggered_rules_raw)]

        confidence_raw = data.get('rule_confidence', data.get('confidence', 0))
        try:
            rule_confidence = float(confidence_raw)
        except (TypeError, ValueError):
            rule_confidence = 0.0

        return {
            'risk_score': risk_score,
            'triggered_rules': triggered_rules,
            'rule_confidence': rule_confidence,
            'source': str(data.get('source') or 'upstream_api')
        }

    def _fallback_result(self, case_data: Dict[str, Any], reason: str) -> Dict[str, Any]:
        risk_score = self._calculate_risk_score(case_data)
        triggered_rules = self._get_triggered_rules(case_data, risk_score)
        logger.warning("Rule engine fallback used: %s", reason)
        return {
            'status': 'success',
            'data': {
                'risk_score': risk_score,
                'triggered_rules': triggered_rules,
                'rule_confidence': 0.5,
                'source': 'heuristic_fallback'
            }
        }

    def _calculate_risk_score(self, case_data: Dict[str, Any]) -> float:
        """Calculate risk score based on case data."""
        score = 0.0
        
        # Amount risk
        amount = case_data.get('amount', 0)
        if amount > 100000:
            score += 30
        elif amount > 50000:
            score += 15
        
        # Device risk
        device_risk = case_data.get('device_risk', 'LOW')
        if device_risk == 'HIGH':
            score += 25
        elif device_risk == 'MEDIUM':
            score += 10
        
        # User label
        user_label = case_data.get('user_label', 'unknown')
        if user_label == 'new_user':
            score += 20
        elif user_label == 'suspicious':
            score += 35
        
        # Country risk
        country = case_data.get('country', 'US')
        high_risk_countries = ['KP', 'IR', 'SY', 'CU']
        if country in high_risk_countries:
            score += 40
        
        return min(score, 100.0)
    
    def _get_triggered_rules(self, case_data: Dict[str, Any], risk_score: float) -> List[str]:
        """Get triggered rules."""
        rules = []
        
        amount = case_data.get('amount', 0)
        if amount > 100000:
            rules.append('RULE_HIGH_AMOUNT')
        
        device_risk = case_data.get('device_risk', 'LOW')
        if device_risk == 'HIGH':
            rules.append('RULE_HIGH_DEVICE_RISK')
        
        user_label = case_data.get('user_label', 'unknown')
        if user_label == 'new_user':
            rules.append('RULE_NEW_USER')
        elif user_label == 'suspicious':
            rules.append('RULE_SUSPICIOUS_USER')
        
        country = case_data.get('country', 'US')
        high_risk_countries = ['KP', 'IR', 'SY', 'CU']
        if country in high_risk_countries:
            rules.append('RULE_HIGH_RISK_COUNTRY')
        
        return rules


class AnalyzeSimilarCasesTool(Tool):
    """Tool to analyze similar cases."""
    
    def __init__(self):
        super().__init__(
            name="analyze_similar_cases",
            description="Analyze similar cases to understand patterns and outcomes"
        )
    
    def execute(self, similar_cases: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """
        Analyze similar cases.
        
        Args:
            similar_cases: List of similar cases
            
        Returns:
            Analysis of similar cases
        """
        try:
            if not similar_cases:
                return {
                    'status': 'success',
                    'data': {
                        'total_cases': 0,
                        'approval_rate': 0.0,
                        'rejection_rate': 0.0,
                        'patterns': []
                    }
                }
            
            # Analyze outcomes
            approved = sum(1 for case in similar_cases if case.get('case_data', {}).get('final_decision') == 'APPROVE')
            rejected = sum(1 for case in similar_cases if case.get('case_data', {}).get('final_decision') == 'REJECT')
            total = len(similar_cases)
            
            approval_rate = approved / total if total > 0 else 0.0
            rejection_rate = rejected / total if total > 0 else 0.0
            
            # Extract patterns
            patterns = self._extract_patterns(similar_cases)
            
            return {
                'status': 'success',
                'data': {
                    'total_cases': total,
                    'approval_rate': approval_rate,
                    'rejection_rate': rejection_rate,
                    'patterns': patterns
                }
            }
        except Exception as e:
            logger.error(f"Error analyzing similar cases: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'data': {'total_cases': 0, 'approval_rate': 0.0, 'rejection_rate': 0.0, 'patterns': []}
            }
    
    def _extract_patterns(self, similar_cases: List[Dict[str, Any]]) -> List[str]:
        """Extract patterns from similar cases."""
        patterns = []
        
        if not similar_cases:
            return patterns
        
        # Check if all similar cases have same decision
        decisions = [case.get('case_data', {}).get('final_decision') for case in similar_cases]
        if all(d == 'APPROVE' for d in decisions):
            patterns.append('All similar cases were approved')
        elif all(d == 'REJECT' for d in decisions):
            patterns.append('All similar cases were rejected')
        
        # Check risk levels
        risk_levels = [case.get('case_data', {}).get('risk_level') for case in similar_cases]
        if risk_levels:
            most_common = max(set(risk_levels), key=risk_levels.count)
            patterns.append(f'Most similar cases have {most_common} risk level')
        
        return patterns


class QueryTransactionHistoryTool(Tool):
    """Tool to query transaction history."""
    
    def __init__(self):
        super().__init__(
            name="query_transaction_history",
            description="Query user's transaction history to understand patterns"
        )
        self.history_url = os.getenv('TRANSACTION_HISTORY_URL', '').strip()
        self.history_token = os.getenv('TRANSACTION_HISTORY_TOKEN', '').strip()
        self.timeout_seconds = int(os.getenv('TRANSACTION_HISTORY_TIMEOUT_SECONDS', '5'))
        self.allow_fallback = os.getenv('AGENT_TOOL_ALLOW_FALLBACK', 'false').lower() == 'true'
    
    def execute(self, user_id: Optional[int] = None, limit: int = 10, **kwargs) -> Dict[str, Any]:
        """
        Query transaction history.
        
        Args:
            user_id: User ID
            limit: Number of transactions to retrieve
            
        Returns:
            Transaction history
        """
        try:
            if not user_id:
                return {
                    'status': 'success',
                    'data': {
                        'transactions': [],
                        'count': 0,
                        'average_amount': 0.0,
                        'approval_rate': 0.0
                    }
                }
            
            if not self.history_url:
                message = "TRANSACTION_HISTORY_URL is not configured"
                if self.allow_fallback:
                    logger.warning("Transaction history fallback used: %s", message)
                    return {'status': 'success', 'data': self._empty_history()}
                return {
                    'status': 'error',
                    'error': message,
                    'data': self._empty_history()
                }

            headers = {'Content-Type': 'application/json'}
            if self.history_token:
                headers['Authorization'] = f'Bearer {self.history_token}'

            response = requests.post(
                self.history_url,
                json={'user_id': user_id, 'limit': limit},
                headers=headers,
                timeout=self.timeout_seconds
            )
            response.raise_for_status()
            payload = response.json()

            if isinstance(payload, dict) and payload.get('status') == 'error':
                raise RuntimeError(str(payload.get('message') or 'Transaction history service returned error'))

            data = payload.get('data') if isinstance(payload, dict) and isinstance(payload.get('data'), dict) else payload
            normalized = self._normalize_history(data, limit)
            
            return {
                'status': 'success',
                'data': normalized
            }
        except Exception as e:
            logger.error(f"Error querying transaction history: {str(e)}")
            if self.allow_fallback:
                logger.warning("Transaction history fallback used after error")
                return {'status': 'success', 'data': self._empty_history()}
            return {
                'status': 'error',
                'error': str(e),
                'data': self._empty_history()
            }

    def _normalize_history(self, data: Any, limit: int) -> Dict[str, Any]:
        if not isinstance(data, dict):
            return self._empty_history()

        transactions_raw = data.get('transactions', [])
        transactions: List[Dict[str, Any]] = []

        if isinstance(transactions_raw, list):
            for tx in transactions_raw[:limit]:
                if not isinstance(tx, dict):
                    continue
                normalized = dict(tx)
                status = str(normalized.get('status', '')).upper()
                if status in {'APPROVE', 'APPROVED'}:
                    normalized['status'] = 'APPROVED'
                elif status in {'REJECT', 'REJECTED'}:
                    normalized['status'] = 'REJECTED'
                transactions.append(normalized)

        count = len(transactions)

        average_amount_raw = data.get('average_amount')
        if average_amount_raw is None and count > 0:
            amount_values = []
            for tx in transactions:
                try:
                    amount_values.append(float(tx.get('amount', 0)))
                except (TypeError, ValueError):
                    continue
            average_amount = sum(amount_values) / len(amount_values) if amount_values else 0.0
        else:
            try:
                average_amount = float(average_amount_raw or 0)
            except (TypeError, ValueError):
                average_amount = 0.0

        approval_rate_raw = data.get('approval_rate')
        if approval_rate_raw is None and count > 0:
            approved = sum(1 for tx in transactions if tx.get('status') == 'APPROVED')
            approval_rate = approved / count
        else:
            try:
                approval_rate = float(approval_rate_raw or 0)
            except (TypeError, ValueError):
                approval_rate = 0.0

        return {
            'transactions': transactions,
            'count': count,
            'average_amount': average_amount,
            'approval_rate': approval_rate
        }

    def _empty_history(self) -> Dict[str, Any]:
        return {
            'transactions': [],
            'count': 0,
            'average_amount': 0.0,
            'approval_rate': 0.0
        }


def get_tools(retriever) -> Dict[str, Tool]:
    """Get all available tools."""
    return {
        'retrieve_similar_cases': RetrieveSimilarCasesTool(retriever),
        'query_rule_engine': QueryRuleEngineTool(),
        'analyze_similar_cases': AnalyzeSimilarCasesTool(),
        'query_transaction_history': QueryTransactionHistoryTool()
    }
