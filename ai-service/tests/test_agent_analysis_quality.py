import json
import os
import unittest
from unittest.mock import patch

from src.agent.agent import AIAgent


class DummyRetriever:
    def retrieve_similar_cases(self, case_data, top_k=2, similarity_threshold=0.5):
        return [
            {
                "similarity": 0.83,
                "match_source": "rag",
                "case_data": {
                    "id": 9001,
                    "biz_transaction_id": "SIM-9001",
                    "amount": 4900,
                    "currency": "USD",
                    "country": "US",
                    "risk_level": "MEDIUM",
                    "final_decision": "REJECT",
                },
            }
        ][:top_k]

    def retrieve_by_criteria(self, criteria, limit=10):
        return []


class DummyPromptManager:
    def get_active_prompt(self):
        return {
            "version": "v-test",
            "system_prompt": "You are a risk analyst.",
            "user_prompt_template": (
                "amount={amount}, currency={currency}, country={country}, "
                "device={device_risk}, rule={rule_score}, rules={triggered_rules}, "
                "similar={similar_cases}"
            ),
        }

    def get_prompt_by_version(self, prompt_version):
        return self.get_active_prompt()

    def format_prompt(self, template, **kwargs):
        return template.format(**kwargs)


class NonJsonLLM:
    def generate_with_context(self, system_prompt, user_prompt, **kwargs):
        if system_prompt == "You are a JSON formatter.":
            raise RuntimeError("formatter unavailable")
        return "analysis result: high risk, please manual review"


class GenericJsonLLM:
    def generate_with_context(self, system_prompt, user_prompt, **kwargs):
        return json.dumps(
            {
                "risk_level": "MEDIUM",
                "confidence_score": 0.51,
                "key_risk_points": ["risk exists, please review"],
                "suggested_action": "MANUAL_REVIEW",
                "reasoning": "risk exists, please review",
                "similar_cases_analysis": "none",
                "rule_engine_alignment": "none",
            },
            ensure_ascii=False,
        )


class AgentAnalysisQualityTest(unittest.TestCase):
    def _build_case_data(self):
        return {
            "id": 1001,
            "amount": 5200,
            "currency": "USD",
            "country": "US",
            "device_risk": "HIGH",
            "user_label": "new_user",
            "risk_score": 0.82,
            "triggered_rules": ["RULE_HIGH_DEVICE_RISK", "RULE_NEW_USER"],
        }

    @patch.dict(os.environ, {"AI_DECISION_MODE": "llm_only", "AI_FAIL_FAST": "false", "AI_ALLOW_EVIDENCE_FALLBACK": "true"}, clear=False)
    def test_non_json_output_is_repaired_to_evidence_based_analysis(self):
        agent = AIAgent(NonJsonLLM(), DummyPromptManager(), DummyRetriever())
        result = agent.analyze_case(self._build_case_data())

        reasoning = result.get("reasoning", "")
        self.assertTrue(any(k in reasoning for k in ["amount", "金额", "閲戦"]))
        self.assertTrue(any(k in reasoning for k in ["Rule score", "规则引擎评分", "瑙勫垯寮曟搸璇勫垎"]))
        self.assertGreaterEqual(len(result.get("key_risk_points", [])), 3)
        similar_cases_analysis = result.get("similar_cases_analysis", "")
        self.assertTrue(any(k in similar_cases_analysis for k in ["similar cases", "相似案例", "鐩镐技妗堜欢"]))

    @patch.dict(os.environ, {"AI_DECISION_MODE": "llm_only", "AI_FAIL_FAST": "false", "AI_ALLOW_EVIDENCE_FALLBACK": "true"}, clear=False)
    def test_generic_json_is_enriched_with_concrete_evidence(self):
        agent = AIAgent(GenericJsonLLM(), DummyPromptManager(), DummyRetriever())
        result = agent.analyze_case(self._build_case_data())

        reasoning = result.get("reasoning", "")
        self.assertTrue(any(k in reasoning for k in ["Evidence-driven assessment", "证据驱动分析", "璇佹嵁椹卞姩鍒嗘瀽"]))
        self.assertGreaterEqual(len(result.get("key_risk_points", [])), 3)
        self.assertTrue(
            any(
                ("Transaction amount" in p)
                or ("Rule score" in p)
                or ("交易金额" in p)
                or ("规则评分" in p)
                or ("浜ゆ槗閲戦" in p)
                or ("瑙勫垯璇勫垎" in p)
                for p in result.get("key_risk_points", [])
            )
        )


if __name__ == "__main__":
    unittest.main()
