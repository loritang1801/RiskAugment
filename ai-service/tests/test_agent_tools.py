import os
import unittest
from unittest.mock import patch, Mock

from src.agent.tools import QueryRuleEngineTool, QueryTransactionHistoryTool


class QueryRuleEngineToolTest(unittest.TestCase):
    @patch.dict(
        os.environ,
        {
            "RULE_ENGINE_URL": "http://rule-engine.local/evaluate",
            "RULE_ENGINE_TIMEOUT_SECONDS": "3",
            "AGENT_TOOL_ALLOW_FALLBACK": "false",
        },
        clear=False,
    )
    @patch("src.agent.tools.requests.post")
    def test_rule_engine_success(self, mock_post: Mock):
        mock_resp = Mock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = {
            "status": "success",
            "data": {
                "risk_score": 78.5,
                "triggered_rules": ["RULE_A", "RULE_B"],
                "rule_confidence": 0.92,
            },
        }
        mock_post.return_value = mock_resp

        tool = QueryRuleEngineTool()
        result = tool.execute(case_data={"amount": 10000, "country": "US"})

        self.assertEqual(result["status"], "success")
        self.assertAlmostEqual(result["data"]["risk_score"], 78.5)
        self.assertEqual(result["data"]["triggered_rules"], ["RULE_A", "RULE_B"])
        self.assertAlmostEqual(result["data"]["rule_confidence"], 0.92)

    @patch.dict(
        os.environ,
        {
            "RULE_ENGINE_URL": "",
            "AGENT_TOOL_ALLOW_FALLBACK": "false",
        },
        clear=False,
    )
    def test_rule_engine_no_url_returns_error(self):
        tool = QueryRuleEngineTool()
        result = tool.execute(case_data={"amount": 10000})

        self.assertEqual(result["status"], "error")
        self.assertIn("RULE_ENGINE_URL", result["error"])

    @patch.dict(
        os.environ,
        {
            "RULE_ENGINE_URL": "",
            "AGENT_TOOL_ALLOW_FALLBACK": "true",
        },
        clear=False,
    )
    def test_rule_engine_fallback_enabled(self):
        tool = QueryRuleEngineTool()
        result = tool.execute(case_data={"amount": 200000, "device_risk": "HIGH", "country": "KP"})

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["data"]["source"], "heuristic_fallback")
        self.assertGreater(result["data"]["risk_score"], 0)
        self.assertTrue(result["data"]["triggered_rules"])


class QueryTransactionHistoryToolTest(unittest.TestCase):
    @patch.dict(
        os.environ,
        {
            "TRANSACTION_HISTORY_URL": "http://history.local/query",
            "TRANSACTION_HISTORY_TIMEOUT_SECONDS": "3",
            "AGENT_TOOL_ALLOW_FALLBACK": "false",
        },
        clear=False,
    )
    @patch("src.agent.tools.requests.post")
    def test_history_success(self, mock_post: Mock):
        mock_resp = Mock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = {
            "status": "success",
            "data": {
                "transactions": [
                    {"id": 1, "amount": 100.0, "status": "approve"},
                    {"id": 2, "amount": 300.0, "status": "rejected"},
                ]
            },
        }
        mock_post.return_value = mock_resp

        tool = QueryTransactionHistoryTool()
        result = tool.execute(user_id=1001, limit=10)

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["data"]["count"], 2)
        self.assertAlmostEqual(result["data"]["average_amount"], 200.0)
        self.assertAlmostEqual(result["data"]["approval_rate"], 0.5)
        self.assertEqual(result["data"]["transactions"][0]["status"], "APPROVED")
        self.assertEqual(result["data"]["transactions"][1]["status"], "REJECTED")

    @patch.dict(
        os.environ,
        {
            "TRANSACTION_HISTORY_URL": "",
            "AGENT_TOOL_ALLOW_FALLBACK": "false",
        },
        clear=False,
    )
    def test_history_no_url_returns_error(self):
        tool = QueryTransactionHistoryTool()
        result = tool.execute(user_id=1001, limit=10)

        self.assertEqual(result["status"], "error")
        self.assertIn("TRANSACTION_HISTORY_URL", result["error"])

    @patch.dict(
        os.environ,
        {
            "TRANSACTION_HISTORY_URL": "",
            "AGENT_TOOL_ALLOW_FALLBACK": "true",
        },
        clear=False,
    )
    def test_history_fallback_enabled(self):
        tool = QueryTransactionHistoryTool()
        result = tool.execute(user_id=1001, limit=10)

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["data"]["count"], 0)
        self.assertEqual(result["data"]["transactions"], [])


if __name__ == "__main__":
    unittest.main()
