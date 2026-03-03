"""
AI analysis service for risk case analysis.
"""

import logging
import json
import time
from typing import Dict, Any, Optional
from src.database.models import AIPromptLog
from src.database.connection import db

logger = logging.getLogger(__name__)


class AIAnalysisService:
    """Service for AI-powered risk analysis."""
    
    def __init__(self, llm_client, prompt_manager, retriever):
        """
        Initialize AI analysis service.
        
        Args:
            llm_client: LLM client instance
            prompt_manager: Prompt manager instance
            retriever: RAG retriever instance
        """
        self.llm_client = llm_client
        self.prompt_manager = prompt_manager
        self.retriever = retriever
    
    def analyze_case(self, case_data: Dict[str, Any], prompt_version: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze a risk case using AI.
        
        Args:
            case_data: Case data to analyze
            prompt_version: Specific prompt version to use (optional)
            
        Returns:
            Analysis result with risk assessment
        """
        start_time = time.time()
        case_id = case_data.get('id')
        ai_decision_id = None
        
        try:
            # Get prompt template
            if prompt_version:
                prompt = self.prompt_manager.get_prompt_by_version(prompt_version)
            else:
                prompt = self.prompt_manager.get_active_prompt()
            
            if not prompt:
                raise ValueError("No prompt template available")
            
            # Retrieve similar cases
            retrieval_start = time.time()
            similar_cases = self.retriever.retrieve_similar_cases(case_data)
            retrieval_time = int((time.time() - retrieval_start) * 1000)
            
            # Format similar cases for prompt
            similar_cases_text = self._format_similar_cases(similar_cases)
            
            # Format user prompt
            user_prompt = self.prompt_manager.format_prompt(
                prompt['user_prompt_template'],
                amount=case_data.get('amount', 0),
                currency=case_data.get('currency', 'USD'),
                country=case_data.get('country', 'Unknown'),
                device_risk=case_data.get('device_risk', 'UNKNOWN'),
                user_label=case_data.get('user_label', 'unknown'),
                triggered_rules=', '.join(case_data.get('triggered_rules', [])),
                similar_cases=similar_cases_text,
                rule_results=json.dumps(case_data.get('rule_engine_score', 0))
            )
            
            # Call LLM
            llm_start = time.time()
            llm_response = self.llm_client.generate_with_context(
                system_prompt=prompt['system_prompt'],
                user_prompt=user_prompt,
                temperature=0.7,
                max_tokens=1000
            )
            llm_time = int((time.time() - llm_start) * 1000)
            
            # Parse LLM response
            analysis = self._parse_llm_response(llm_response)
            
            # Add metadata
            total_time = int((time.time() - start_time) * 1000)
            analysis['metadata'] = {
                'prompt_version': prompt['version'],
                'retrieval_time_ms': retrieval_time,
                'llm_call_time_ms': llm_time,
                'total_time_ms': total_time,
                'similar_cases_count': len(similar_cases)
            }
            
            # Log AI call
            if case_id:
                self._log_ai_call(
                    case_id=case_id,
                    prompt_version=prompt['version'],
                    system_prompt=prompt['system_prompt'],
                    user_prompt=user_prompt,
                    llm_response=llm_response,
                    latency_ms=total_time
                )
            
            logger.info(f"Analysis completed in {total_time}ms")
            return analysis
        
        except Exception as e:
            logger.error(f"Error analyzing case: {str(e)}")
            raise
    
    def _format_similar_cases(self, similar_cases: list) -> str:
        """Format similar cases for prompt."""
        if not similar_cases:
            return "No similar cases found."
        
        lines = []
        for i, case in enumerate(similar_cases, 1):
            case_data = case.get('case_data', {})
            similarity = case.get('similarity', 0)
            lines.append(
                f"{i}. Case ID: {case_data.get('id')}, "
                f"Amount: {case_data.get('amount')} {case_data.get('currency')}, "
                f"Risk Level: {case_data.get('risk_level')}, "
                f"Similarity: {similarity:.2%}"
            )
        
        return "\n".join(lines)
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response."""
        try:
            # Try to parse as JSON
            analysis = json.loads(response)
            return analysis
        except json.JSONDecodeError:
            # If not JSON, create structured response
            logger.warning("LLM response is not valid JSON, creating default response")
            return {
                'risk_level': 'MEDIUM',
                'confidence_score': 0.5,
                'key_risk_points': ['Unable to parse LLM response'],
                'suggested_action': 'MANUAL_REVIEW',
                'reasoning': response
            }
    
    def _log_ai_call(self, case_id: int, prompt_version: str, system_prompt: str, 
                     user_prompt: str, llm_response: str, latency_ms: int) -> None:
        """Log AI call to database."""
        try:
            log_entry = AIPromptLog(
                case_id=case_id,
                prompt_version=prompt_version,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                llm_response=llm_response,
                llm_model='claude-3-sonnet',
                latency_ms=latency_ms
            )
            db.session.add(log_entry)
            db.session.commit()
            logger.info(f"AI call logged for case {case_id}")
        except Exception as e:
            logger.error(f"Error logging AI call: {str(e)}")
            db.session.rollback()
    
    def batch_analyze(self, cases: list, prompt_version: Optional[str] = None) -> list:
        """
        Analyze multiple cases.
        
        Args:
            cases: List of case data
            prompt_version: Specific prompt version to use
            
        Returns:
            List of analysis results
        """
        results = []
        for i, case in enumerate(cases):
            try:
                result = self.analyze_case(case, prompt_version)
                results.append({
                    'case_id': case.get('id'),
                    'analysis': result,
                    'status': 'success'
                })
            except Exception as e:
                logger.error(f"Error analyzing case {i}: {str(e)}")
                results.append({
                    'case_id': case.get('id'),
                    'error': str(e),
                    'status': 'error'
                })
        
        return results


def get_ai_service(llm_client, prompt_manager, retriever) -> AIAnalysisService:
    """Get AI analysis service."""
    return AIAnalysisService(llm_client, prompt_manager, retriever)
