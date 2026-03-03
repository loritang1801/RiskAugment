"""
AI Agent for orchestrating tools and LLM calls.
"""

import logging
import json
import time
import os
import re
from typing import Dict, Any, Optional, List
from src.agent.tools import get_tools
from src.agent.executor import ToolExecutor

logger = logging.getLogger(__name__)


class AIAgent:
    """AI Agent that orchestrates tools and LLM calls."""
    
    def __init__(self, llm_client, prompt_manager, retriever):
        """
        Initialize AI Agent.
        
        Args:
            llm_client: LLM client instance
            prompt_manager: Prompt manager instance
            retriever: RAG retriever instance
        """
        self.llm_client = llm_client
        self.prompt_manager = prompt_manager
        self.retriever = retriever
        self.tools = get_tools(retriever)
        self.executor = ToolExecutor(timeout_seconds=30, max_workers=4)
        decision_mode = os.getenv('AI_DECISION_MODE', 'llm_only').lower()
        self.decision_mode = decision_mode if decision_mode in {'llm_only', 'hybrid'} else 'llm_only'
        self.fail_fast = os.getenv('AI_FAIL_FAST', 'true').lower() == 'true'
        self.similar_top_k = int(os.getenv('AGENT_SIMILAR_TOP_K', '2'))
        self.llm_temperature = float(os.getenv('AGENT_LLM_TEMPERATURE', '0.2'))
        self.llm_max_tokens = int(os.getenv('AGENT_LLM_MAX_TOKENS', '1200'))
    
    def analyze_case(self, case_data: Dict[str, Any], prompt_version: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze a case using agent workflow.
        
        Args:
            case_data: Case data to analyze
            prompt_version: Specific prompt version to use
            
        Returns:
            Analysis result
        """
        start_time = time.time()
        
        try:
            rule_data = {}
            if self.decision_mode != 'llm_only':
                logger.info("Step 1: Querying rule engine (hybrid mode)...")
                rule_result = self.executor.execute_tool(
                    'query_rule_engine',
                    self.tools['query_rule_engine'].execute,
                    case_data=case_data
                )

                if rule_result['status'] != 'success':
                    logger.error("Rule engine query failed in hybrid mode")
                    if self.fail_fast:
                        raise RuntimeError("Rule engine query failed")
                else:
                    rule_data = rule_result['data']
            else:
                # In llm_only mode, pass-through existing score/rules from case data if provided.
                raw_rules = case_data.get('triggered_rules')
                if isinstance(raw_rules, list):
                    triggered_rules = [str(r) for r in raw_rules]
                elif isinstance(raw_rules, dict):
                    triggered_rules = [str(k) for k in raw_rules.keys()]
                elif raw_rules is None:
                    triggered_rules = []
                else:
                    triggered_rules = [str(raw_rules)]

                rule_data = {
                    'risk_score': case_data.get('rule_engine_score') or case_data.get('risk_score') or 0,
                    'triggered_rules': triggered_rules,
                    'rule_confidence': case_data.get('rule_confidence', 0),
                    'source': 'case_data'
                }
            
            # Step 2: Retrieve similar cases
            logger.info("Step 2: Retrieving similar cases...")
            # Do not run retrieval in thread pool to avoid Flask app context loss.
            retrieval_result = self.tools['retrieve_similar_cases'].execute(
                case_data=case_data,
                top_k=max(1, self.similar_top_k)
            )
            
            similar_cases = retrieval_result['data']['similar_cases'] if retrieval_result['status'] == 'success' else []
            
            # Step 3: Analyze similar cases
            logger.info("Step 3: Analyzing similar cases...")
            analysis_result = self.executor.execute_tool(
                'analyze_similar_cases',
                self.tools['analyze_similar_cases'].execute,
                similar_cases=similar_cases
            )
            
            similar_analysis = analysis_result['data'] if analysis_result['status'] == 'success' else {}
            
            # Step 4: Query transaction history (hybrid mode only; tool is mock for now)
            transaction_history = {}
            if self.decision_mode != 'llm_only':
                logger.info("Step 4: Querying transaction history (hybrid mode)...")
                user_id = case_data.get('user_id')
                history_result = self.executor.execute_tool(
                    'query_transaction_history',
                    self.tools['query_transaction_history'].execute,
                    user_id=user_id,
                    limit=10
                )
                if history_result['status'] == 'success':
                    transaction_history = history_result['data']
            
            # Step 5: Call LLM with all context
            logger.info("Step 5: Calling LLM for final analysis...")
            llm_analysis = self._call_llm_with_context(
                case_data=case_data,
                rule_data=rule_data,
                similar_cases=similar_cases,
                similar_analysis=similar_analysis,
                transaction_history=transaction_history,
                prompt_version=prompt_version
            )
            
            # Add execution metrics
            total_time = int((time.time() - start_time) * 1000)
            llm_analysis['execution_metrics'] = {
                'total_time_ms': total_time,
                'tool_executions': self.executor.get_execution_summary()
            }
            
            return llm_analysis

        except Exception as e:
            logger.error(f"Error in agent analysis: {str(e)}")
            if self.fail_fast:
                raise
            return self._get_default_analysis()
    
    def _call_llm_with_context(
        self,
        case_data: Dict[str, Any],
        rule_data: Dict[str, Any],
        similar_cases: List[Dict[str, Any]],
        similar_analysis: Dict[str, Any],
        transaction_history: Dict[str, Any],
        prompt_version: Optional[str] = None
    ) -> Dict[str, Any]:
        """Call LLM with full context."""
        try:
            # Get prompt template
            if prompt_version:
                prompt = self.prompt_manager.get_prompt_by_version(prompt_version)
            else:
                prompt = self.prompt_manager.get_active_prompt()
            
            if not prompt:
                logger.warning("No prompt template available, using default")
                if self.fail_fast:
                    raise RuntimeError("No active prompt template available")
                return self._get_default_analysis()
            
            compact_context = self._build_compact_context(
                case_data=case_data,
                rule_data=rule_data,
                similar_cases=similar_cases,
                similar_analysis=similar_analysis,
                transaction_history=transaction_history
            )
            system_prompt = (
                "You are a risk-analysis engine. Return JSON only with no markdown. "
                "All explanatory fields must be Chinese; enums must remain English."
            )
            user_prompt = (
                "Analyze the following case context and return STRICT JSON with keys: "
                "risk_level, confidence_score, key_risk_points, suggested_action, reasoning, "
                "similar_cases_analysis, rule_engine_alignment. "
                "Rules: risk_level in [LOW, MEDIUM, HIGH]; suggested_action in [APPROVE, REJECT, MANUAL_REVIEW]; "
                "key_risk_points must include 3-4 concrete evidence items; reasoning must contain 4-6 sentences.\n\n"
                f"case_context={compact_context}"
            )

            # Call LLM with hard JSON preference to improve parse stability.
            llm_response = self.llm_client.generate_with_context(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.0,
                max_tokens=min(self.llm_max_tokens, 700),
                response_format='json_object'
            )
            
            # Parse response
            analysis = self._parse_llm_response(llm_response)
            if str(analysis.get('_response_path')) == 'evidence_fallback':
                retry_prompt = (
                    "Previous output failed strict parsing. Regenerate and return ONLY valid JSON with the same keys.\n\n"
                    f"case_context={compact_context}"
                )
                retry_response = self.llm_client.generate_with_context(
                    system_prompt=system_prompt,
                    user_prompt=retry_prompt,
                    temperature=0.0,
                    max_tokens=min(self.llm_max_tokens, 700),
                    response_format='json_object'
                )
                retry_analysis = self._parse_llm_response(retry_response)
                if str(retry_analysis.get('_response_path')) != 'evidence_fallback':
                    analysis = retry_analysis
            analysis = self._post_process_analysis(
                analysis=analysis,
                case_data=case_data,
                rule_data=rule_data,
                similar_cases=similar_cases,
                similar_analysis=similar_analysis,
                transaction_history=transaction_history
            )
            analysis.setdefault(
                'similar_cases_analysis',
                self._build_similar_cases_analysis(similar_cases, similar_analysis)
            )
            analysis.setdefault(
                'rule_engine_alignment',
                self._build_rule_alignment(rule_data)
            )
            details = analysis.get('similar_cases_details')
            if not isinstance(details, list) or not details:
                analysis['similar_cases_details'] = self._build_similar_cases_details(similar_cases)
            
            # Add metadata
            response_path = str(analysis.pop('_response_path', 'llm_structured'))
            analysis['metadata'] = {
                'prompt_version': prompt.get('version', 'unknown'),
                'rule_score': rule_data.get('risk_score', 0),
                'similar_cases_count': len(similar_cases),
                'similar_cases_approval_rate': similar_analysis.get('approval_rate', 0),
                'transaction_count': transaction_history.get('count', 0),
                'transaction_approval_rate': transaction_history.get('approval_rate', 0),
                'decision_mode': self.decision_mode,
                'response_path': response_path
            }
            analysis.setdefault('analysis_source', f"llm:{os.getenv('LLM_PROVIDER', 'openai')}")
            analysis.setdefault('analysis_model', os.getenv('LLM_MODEL', 'gpt-4o-mini'))
            
            return analysis
        
        except Exception as e:
            logger.error(f"Error calling LLM: {str(e)}")
            if self.fail_fast:
                raise
            return self._get_default_analysis()

    def _post_process_analysis(
        self,
        analysis: Dict[str, Any],
        case_data: Dict[str, Any],
        rule_data: Dict[str, Any],
        similar_cases: List[Dict[str, Any]],
        similar_analysis: Dict[str, Any],
        transaction_history: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Normalize and enrich analysis payload to avoid generic/template content."""
        result = dict(analysis or {})
        evidence = self._build_evidence_fallback(
            case_data=case_data,
            rule_data=rule_data,
            similar_cases=similar_cases,
            similar_analysis=similar_analysis,
            transaction_history=transaction_history
        )
        original_path = str(result.get('_response_path') or 'llm_structured')
        used_evidence_fallback = False

        risk_level = str(result.get('risk_level') or '').upper()
        result['risk_level'] = risk_level if risk_level in {'LOW', 'MEDIUM', 'HIGH'} else evidence['risk_level']

        action = str(result.get('suggested_action') or '').upper()
        result['suggested_action'] = (
            action if action in {'APPROVE', 'REJECT', 'MANUAL_REVIEW'} else evidence['suggested_action']
        )

        try:
            confidence = float(result.get('confidence_score'))
        except (TypeError, ValueError):
            confidence = evidence['confidence_score']
        result['confidence_score'] = round(max(0.0, min(1.0, confidence)), 2)

        points = result.get('key_risk_points')
        normalized_points: List[str] = []
        if isinstance(points, list):
            normalized_points = [str(p).strip() for p in points if str(p).strip()]
        elif isinstance(points, str) and points.strip():
            normalized_points = [points.strip()]
        if len(normalized_points) < 3 or any(self._is_generic_text(p) for p in normalized_points):
            normalized_points = evidence['key_risk_points']
            used_evidence_fallback = True
        result['key_risk_points'] = normalized_points[:4]

        reasoning = str(result.get('reasoning') or '').strip()
        if original_path == 'evidence_fallback' or len(reasoning) < 40 or self._is_generic_text(reasoning):
            reasoning = evidence['reasoning']
            used_evidence_fallback = True
        result['reasoning'] = reasoning

        similar_cases_analysis = str(result.get('similar_cases_analysis') or '').strip()
        if len(similar_cases_analysis) < 25 or self._is_generic_text(similar_cases_analysis):
            similar_cases_analysis = evidence['similar_cases_analysis']
            used_evidence_fallback = True
        result['similar_cases_analysis'] = similar_cases_analysis

        rule_alignment = str(result.get('rule_engine_alignment') or '').strip()
        if len(rule_alignment) < 16 or self._is_generic_text(rule_alignment):
            rule_alignment = self._build_rule_alignment(rule_data)
        result['rule_engine_alignment'] = rule_alignment
        if used_evidence_fallback:
            # Keep decision fields consistent with fallback evidence synthesis.
            result['risk_level'] = evidence['risk_level']
            result['suggested_action'] = evidence['suggested_action']
            result['confidence_score'] = round(float(evidence['confidence_score']), 2)
        result['_response_path'] = 'evidence_fallback' if used_evidence_fallback else original_path

        return result

    def _build_compact_context(
        self,
        case_data: Dict[str, Any],
        rule_data: Dict[str, Any],
        similar_cases: List[Dict[str, Any]],
        similar_analysis: Dict[str, Any],
        transaction_history: Dict[str, Any]
    ) -> str:
        """Build compact JSON context for stable structured generation."""
        top_similar = []
        for case in similar_cases[:3]:
            cd = case.get('case_data') or {}
            top_similar.append({
                'case_id': cd.get('id'),
                'amount': cd.get('amount'),
                'currency': cd.get('currency'),
                'country': cd.get('country'),
                'risk_level': cd.get('risk_level'),
                'similarity': round(float(case.get('similarity', 0) or 0), 4)
            })

        payload = {
            'case': {
                'id': case_data.get('id'),
                'amount': case_data.get('amount'),
                'currency': case_data.get('currency'),
                'country': case_data.get('country'),
                'device_risk': case_data.get('device_risk'),
                'user_label': case_data.get('user_label')
            },
            'rule': {
                'risk_score': rule_data.get('risk_score'),
                'triggered_rules': rule_data.get('triggered_rules') or [],
                'source': rule_data.get('source')
            },
            'similar_cases': top_similar,
            'similar_summary': {
                'count': len(similar_cases),
                'approval_rate': similar_analysis.get('approval_rate', 0)
            },
            'history': {
                'count': transaction_history.get('count', 0),
                'approval_rate': transaction_history.get('approval_rate', 0),
                'average_amount': transaction_history.get('average_amount', 0)
            }
        }
        return json.dumps(payload, ensure_ascii=False, separators=(',', ':'))

    def _is_generic_text(self, text: str) -> bool:
        """Detect low-value placeholder text only; avoid penalizing normal risk narratives."""
        raw = (text or '').strip()
        if not raw:
            return True
        lowered = raw.lower()
        generic_tokens = [
            'model output did not pass structured validation',
            'ai service encountered an error',
            'manual review is recommended',
            'unable to parse',
            'invalid json',
            'template text',
            'parse failed',
            'fallback result',
            'please review manually'
        ]
        return any(token in lowered or token in raw for token in generic_tokens)

    def _build_evidence_fallback(
        self,
        case_data: Dict[str, Any],
        rule_data: Dict[str, Any],
        similar_cases: List[Dict[str, Any]],
        similar_analysis: Dict[str, Any],
        transaction_history: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Synthesize deterministic, case-specific explanation when LLM output is low-quality."""
        amount = self._to_float(case_data.get('amount'), 0.0)
        currency = str(case_data.get('currency') or 'USD')
        country = str(case_data.get('country') or 'UNKNOWN')
        device_risk = str(case_data.get('device_risk') or 'UNKNOWN').upper()
        score_raw = self._to_float(rule_data.get('risk_score'), 0.0)
        score_ratio = score_raw / 100.0 if score_raw > 1 else score_raw
        score_ratio = max(0.0, min(1.0, score_ratio))
        triggered_rules = rule_data.get('triggered_rules') or []
        if not isinstance(triggered_rules, list):
            triggered_rules = [str(triggered_rules)]
        rule_summary = ', '.join(str(r) for r in triggered_rules[:3]) if triggered_rules else 'none'

        sim_count = len(similar_cases)
        approval_rate = self._to_float(similar_analysis.get('approval_rate'), 0.0)
        avg_similarity = (
            sum(self._to_float(item.get('similarity'), 0.0) for item in similar_cases) / sim_count
            if sim_count else 0.0
        )

        tx_count = int(self._to_float(transaction_history.get('count'), 0.0))
        tx_approval = self._to_float(transaction_history.get('approval_rate'), 0.0)
        tx_avg_amount = self._to_float(transaction_history.get('average_amount'), 0.0)
        history_sentence = (
            f'History stats: count={tx_count}, avg_amount={tx_avg_amount:.2f} {currency}, approval_rate={tx_approval:.1%}.'
            if tx_count > 0 else
            'History stats are currently unavailable.'
        )

        if score_ratio >= 0.75 or (amount >= 15000 and device_risk == 'HIGH'):
            risk_level = 'HIGH'
            suggested_action = 'REJECT'
            confidence_score = 0.70
        elif score_ratio >= 0.35 or device_risk in {'MEDIUM', 'HIGH'}:
            risk_level = 'MEDIUM'
            suggested_action = 'MANUAL_REVIEW'
            confidence_score = 0.58
        else:
            risk_level = 'LOW'
            suggested_action = 'APPROVE'
            confidence_score = 0.52

        key_risk_points = [
            f'Transaction amount {amount:.2f} {currency}; country={country}; device_risk={device_risk}.',
            f'Rule score {score_ratio:.2f}; triggered_rules={rule_summary}.',
            f'Similar cases {sim_count}; avg_similarity={avg_similarity:.1%}; approval_rate={approval_rate:.1%}.',
            history_sentence
        ]

        reasoning = (
            f'Evidence-driven assessment: amount {amount:.2f} {currency}, device_risk {device_risk}. '
            f'Rule score {score_ratio:.2f} with rules {rule_summary}. '
            f'Similar-case evidence count {sim_count}, avg_similarity {avg_similarity:.1%}, approval_rate {approval_rate:.1%}. '
            f'{history_sentence} Suggested action is {suggested_action} with risk level {risk_level}.'
        )

        similar_cases_analysis = (
            f'Retrieved {sim_count} similar cases with avg_similarity {avg_similarity:.1%} and approval_rate {approval_rate:.1%}.'
            if sim_count > 0 else
            'No high-confidence similar cases were found; decision is based on direct case and rule features.'
        )

        return {
            'risk_level': risk_level,
            'suggested_action': suggested_action,
            'confidence_score': confidence_score,
            'key_risk_points': key_risk_points,
            'reasoning': reasoning,
            'similar_cases_analysis': similar_cases_analysis
        }

    def _to_float(self, value: Any, default: float = 0.0) -> float:
        try:
            if value is None:
                return default
            return float(value)
        except (TypeError, ValueError):
            return default
    
    def _format_similar_cases(self, similar_cases: List[Dict[str, Any]]) -> str:
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
                f"Decision: {case_data.get('final_decision', 'PENDING')}, "
                f"Similarity: {similarity:.1%}"
            )
        
        return "\n".join(lines)
    
    def _format_transaction_history(self, transaction_history: Dict[str, Any]) -> str:
        """Format transaction history for prompt."""
        transactions = transaction_history.get('transactions', [])
        if not transactions:
            return "No transaction history available."
        
        lines = []
        for i, tx in enumerate(transactions[:5], 1):
            lines.append(
                f"{i}. Amount: {tx.get('amount')} {tx.get('currency')}, "
                f"Country: {tx.get('country')}, "
                f"Status: {tx.get('status')}"
            )
        
        return "\n".join(lines)

    def _build_similar_cases_analysis(
        self,
        similar_cases: List[Dict[str, Any]],
        similar_analysis: Dict[str, Any]
    ) -> str:
        """Build deterministic summary when LLM omits similar case analysis."""
        if not similar_cases:
            return "No high-confidence similar cases were found; decision is based on direct case and rule features."

        approval_rate = float(similar_analysis.get('approval_rate', 0) or 0)
        avg_similarity = sum(float(c.get('similarity', 0) or 0) for c in similar_cases) / len(similar_cases)
        source_counts: Dict[str, int] = {}
        for case in similar_cases:
            source = str(case.get('match_source') or 'rag')
            source_counts[source] = source_counts.get(source, 0) + 1
        source_summary = ", ".join(f"{k}:{v}" for k, v in sorted(source_counts.items()))

        return (
            f"Retrieved {len(similar_cases)} similar cases; avg_similarity={avg_similarity:.1%}; "
            f"approval_rate={approval_rate:.1%}; sources={source_summary}."
        )

    def _build_rule_alignment(self, rule_data: Dict[str, Any]) -> str:
        """Build deterministic rule alignment summary."""
        score = float(rule_data.get('risk_score', 0) or 0)
        triggered_rules = rule_data.get('triggered_rules') or []
        source = str(rule_data.get('source') or 'unknown')

        if not isinstance(triggered_rules, list):
            triggered_rules = [str(triggered_rules)]

        if triggered_rules:
            joined = ', '.join(str(r) for r in triggered_rules)
            if source == 'heuristic_fallback':
                return f"Upstream rule engine unavailable; local heuristic rules used. rule_score={score:.2f}, triggered_rules={joined}."
            if source == 'case_data':
                return f"Rule context comes from case payload. rule_score={score:.2f}, triggered_rules={joined}."
            return f"Aligned with upstream rule engine. rule_score={score:.2f}, triggered_rules={joined}."

        if source == 'heuristic_fallback':
            return f"Upstream rule engine unavailable and no explicit local rules triggered. rule_score={score:.2f}."
        if source == 'case_data':
            return f"No explicit triggered_rules in case payload; used rule score. rule_score={score:.2f}."
        return f"No explicit triggered_rules from upstream. rule_score={score:.2f}."

    def _build_similar_cases_details(self, similar_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        details: List[Dict[str, Any]] = []
        for case in similar_cases:
            case_data = case.get('case_data') or {}
            details.append({
                'case_id': case_data.get('id'),
                'biz_transaction_id': case_data.get('biz_transaction_id'),
                'similarity': round(float(case.get('similarity', 0) or 0), 4),
                'risk_level': case_data.get('risk_level'),
                'final_decision': case_data.get('final_decision'),
                'amount': case_data.get('amount'),
                'currency': case_data.get('currency'),
                'country': case_data.get('country'),
                'match_source': case.get('match_source', 'rag')
            })
        return details

    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response with tolerant fallbacks."""
        def _infer_risk_level(text: str) -> str:
            t = (text or '').lower()
            if 'high' in t:
                return 'HIGH'
            if 'low' in t:
                return 'LOW'
            return 'MEDIUM'

        def _infer_action(text: str) -> str:
            t = (text or '').lower()
            if 'reject' in t or 'block' in t:
                return 'REJECT'
            if 'approve' in t:
                return 'APPROVE'
            return 'MANUAL_REVIEW'

        def _extract_points(text: str) -> List[str]:
            points: List[str] = []
            for line in (text or '').splitlines():
                s = line.strip()
                if not s:
                    continue
                if s.startswith(('-', '*')) or re.match(r'^\d+[.)]\s*', s):
                    points.append(re.sub(r'^[-*\d\.)\s]+', '', s))
                if len(points) >= 3:
                    break
            if points:
                return points
            fragments = [frag.strip() for frag in re.split(r'[.;\n]', text or '') if frag.strip()]
            return fragments[:3]

        content = (response or '').strip()
        if content.startswith('```'):
            content = re.sub(r'^```(?:json)?\s*', '', content, flags=re.IGNORECASE)
            content = re.sub(r'\s*```$', '', content)

        match = re.search(r'\{[\s\S]*\}', content)
        if match:
            content = match.group(0)

        try:
            parsed = json.loads(content)
            if isinstance(parsed, dict):
                parsed['_response_path'] = 'llm_structured'
            return parsed
        except json.JSONDecodeError:
            try:
                repaired = re.sub(r',(\s*[}\]])', r'\1', content)
                parsed = json.loads(repaired)
                if isinstance(parsed, dict):
                    parsed['_response_path'] = 'llm_repaired_json'
                return parsed
            except Exception:
                pass

            # Second-pass normalization: ask the LLM to convert raw output into strict JSON.
            try:
                normalize_prompt = (
                    "Convert the following analysis text to STRICT JSON with keys: "
                    "risk_level, confidence_score, key_risk_points, suggested_action, reasoning, "
                    "similar_cases_analysis, rule_engine_alignment. "
                    "risk_level must be LOW/MEDIUM/HIGH. "
                    "suggested_action must be APPROVE/REJECT/MANUAL_REVIEW. "
                    "Return JSON only.\n\n"
                    f"{response}"
                )
                normalized_text = self.llm_client.generate_with_context(
                    system_prompt="You are a JSON formatter.",
                    user_prompt=normalize_prompt,
                    temperature=0.0,
                    max_tokens=500
                )
                normalized_text = (normalized_text or '').strip()
                if normalized_text.startswith('```'):
                    normalized_text = re.sub(r'^```(?:json)?\s*', '', normalized_text, flags=re.IGNORECASE)
                    normalized_text = re.sub(r'\s*```$', '', normalized_text)
                match2 = re.search(r'\{[\s\S]*\}', normalized_text)
                if match2:
                    normalized_text = match2.group(0)
                parsed = json.loads(normalized_text)
                if isinstance(parsed, dict):
                    parsed['_response_path'] = 'llm_repaired_json'
                return parsed
            except Exception:
                pass

            logger.warning('LLM response is not valid JSON')
            raw_text = (response or '').strip()
            points = _extract_points(raw_text)
            return {
                'risk_level': _infer_risk_level(raw_text),
                'confidence_score': 0.5,
                'key_risk_points': points or ['Model returned non-structured content; extracted readable evidence from raw output.'],
                'suggested_action': _infer_action(raw_text),
                'reasoning': raw_text[:1200] if raw_text else 'Model output did not pass structured validation; evidence fallback was applied.',
                'similar_cases_details': [],
                '_response_path': 'evidence_fallback'
            }

    def _get_default_analysis(self) -> Dict[str, Any]:
        """Get default analysis when agent fails."""
        return {
            'risk_level': 'HIGH',
            'confidence_score': 0.3,
            'key_risk_points': ['AI analysis failed; manual review is recommended.'],
            'suggested_action': 'MANUAL_REVIEW',
            'reasoning': 'AI service encountered an error. Please review manually.',
            'similar_cases_details': [],
            'metadata': {
                'prompt_version': 'unknown',
                'rule_score': 0,
                'similar_cases_count': 0,
                'similar_cases_approval_rate': 0,
                'transaction_count': 0,
                'transaction_approval_rate': 0,
                'response_path': 'evidence_fallback'
            }
        }


def get_agent(llm_client, prompt_manager, retriever) -> AIAgent:
    """Get AI Agent instance."""
    return AIAgent(llm_client, prompt_manager, retriever)
