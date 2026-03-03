"""
RAG (Retrieval-Augmented Generation) retriever for finding similar cases.
"""

import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class Retriever:
    """RAG retriever for finding similar risk cases."""
    
    def __init__(self, db_session, embedding_model=None, top_k: int = 5, similarity_threshold: float = 0.7):
        """
        Initialize retriever.
        
        Args:
            db_session: Database session
            embedding_model: Embedding model instance (optional)
            top_k: Number of top results to return
            similarity_threshold: Minimum similarity threshold
        """
        if embedding_model is None:
            from src.embedding.embedding_model import get_embedding_model
            embedding_model = get_embedding_model()

        self.db_session = db_session
        self.embedding_model = embedding_model
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold
    
    def get_case_by_id(self, case_id: int) -> Optional[Dict[str, Any]]:
        """Get case data by ID."""
        try:
            from src.database.models import RiskCase

            case = self.db_session.query(RiskCase).filter_by(id=case_id).first()
            if not case:
                return None
            return self._case_to_dict(case)
        except Exception as e:
            logger.error(f"Error getting case by id: {str(e)}")
            return None

    def retrieve_similar_cases(
        self,
        query_case: Dict[str, Any],
        top_k: Optional[int] = None,
        similarity_threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve similar cases for a given query case.
        
        Args:
            query_case: Query case data
            
        Returns:
            List of similar cases with similarity scores
        """
        try:
            # Generate query embedding from case features
            query_embedding = self._generate_case_embedding(query_case)
            
            # Query database for similar cases
            similar_cases = self._query_similar_cases(
                query_embedding=query_embedding,
                query_case_id=query_case.get('id'),
                top_k=top_k if top_k is not None else self.top_k,
                similarity_threshold=(
                    similarity_threshold
                    if similarity_threshold is not None
                    else self.similarity_threshold
                )
            )
            
            logger.info(f"Retrieved {len(similar_cases)} similar cases")
            return similar_cases
        except Exception as e:
            logger.error(f"Error retrieving similar cases: {str(e)}")
            raise
    
    def _generate_case_embedding(self, case: Dict[str, Any]) -> List[float]:
        """
        Generate embedding for a case.
        
        Args:
            case: Case data
            
        Returns:
            Embedding vector
        """
        # Create text representation of case
        case_text = self._case_to_text(case)
        
        # Generate embedding
        embedding = self.embedding_model.embed_text(case_text)
        
        return embedding
    
    def _case_to_text(self, case: Dict[str, Any]) -> str:
        """
        Convert case to text representation for embedding.
        
        Args:
            case: Case data
            
        Returns:
            Text representation
        """
        parts = []
        
        # Add key fields
        if 'amount' in case:
            parts.append(f"Amount: {case['amount']}")
        
        if 'currency' in case:
            parts.append(f"Currency: {case['currency']}")
        
        if 'country' in case:
            parts.append(f"Country: {case['country']}")
        
        if 'device_risk' in case:
            parts.append(f"Device Risk: {case['device_risk']}")
        
        if 'user_label' in case:
            parts.append(f"User Label: {case['user_label']}")
        
        if 'risk_level' in case:
            parts.append(f"Risk Level: {case['risk_level']}")
        
        if 'triggered_rules' in case and case['triggered_rules']:
            triggered_rules = case['triggered_rules']
            if isinstance(triggered_rules, list):
                parts.append(f"Triggered Rules: {', '.join(str(r) for r in triggered_rules)}")
            elif isinstance(triggered_rules, dict):
                parts.append(f"Triggered Rules: {', '.join(str(k) for k in triggered_rules.keys())}")
            else:
                parts.append(f"Triggered Rules: {triggered_rules}")
        
        return ". ".join(parts)
    
    def _query_similar_cases(
        self,
        query_embedding: List[float],
        query_case_id: Optional[int] = None,
        top_k: int = 5,
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Query risk cases and rank with embedding similarity.
        
        Args:
            query_embedding: Query embedding vector
            query_case_id: Query case ID (exclude from result)
            top_k: Number of results
            similarity_threshold: Similarity threshold
            
        Returns:
            List of similar cases
        """
        try:
            from src.database.models import RiskCase

            candidates = (
                self.db_session.query(RiskCase)
                .filter(RiskCase.deleted_at.is_(None))
                .all()
            )

            scored: List[Dict[str, Any]] = []
            for candidate in candidates:
                if query_case_id is not None and int(candidate.id) == int(query_case_id):
                    continue

                candidate_dict = self._case_to_dict(candidate)
                candidate_embedding = self._generate_case_embedding(candidate_dict)
                similarity = self.embedding_model.similarity(query_embedding, candidate_embedding)

                if similarity < similarity_threshold:
                    continue

                scored.append({
                    'id': candidate_dict['id'],
                    'similarity': round(float(similarity), 4),
                    'case_data': candidate_dict
                })

            scored.sort(key=lambda item: item['similarity'], reverse=True)
            return scored[:top_k]
        except Exception as e:
            logger.error(f"Error querying similar cases: {str(e)}")
            return []
    
    def retrieve_by_criteria(self, criteria: Dict[str, Any], limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Retrieve cases by specific criteria.
        
        Args:
            criteria: Search criteria (country, risk_level, etc.)
            
        Returns:
            List of matching cases
        """
        try:
            from src.database.models import RiskCase
            
            query = self.db_session.query(RiskCase)
            
            # Apply filters
            if 'country' in criteria:
                query = query.filter_by(country=criteria['country'])
            
            if 'risk_level' in criteria:
                query = query.filter_by(risk_level=criteria['risk_level'])
            
            if 'device_risk' in criteria:
                query = query.filter_by(device_risk=criteria['device_risk'])
            
            if 'user_label' in criteria:
                query = query.filter_by(user_label=criteria['user_label'])
            
            # Limit results
            max_results = limit if limit is not None else self.top_k
            results = query.limit(max_results).all()
            
            # Convert to dict
            return [self._case_to_dict(case) for case in results]
        except Exception as e:
            logger.error(f"Error retrieving by criteria: {str(e)}")
            return []
    
    def _case_to_dict(self, case) -> Dict[str, Any]:
        """Convert case object to dictionary."""
        return {
            'id': case.id,
            'biz_transaction_id': case.biz_transaction_id,
            'amount': float(case.amount),
            'currency': case.currency,
            'country': case.country,
            'device_risk': case.device_risk,
            'user_label': case.user_label,
            'risk_features': case.risk_features,
            'risk_level': case.risk_level,
            'risk_status': case.risk_status,
            'final_decision': case.final_decision,
            'created_at': case.created_at.isoformat() if case.created_at else None
        }
