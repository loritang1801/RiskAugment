import os
import unittest
from unittest.mock import patch

from src.llm.client import OpenAIClient


class OpenAIClientRequestBuilderTest(unittest.TestCase):
    @patch.dict(os.environ, {"BIGMODEL_THINKING_TYPE": "disabled"}, clear=False)
    def test_bigmodel_uses_extra_body_to_disable_thinking(self):
        client = OpenAIClient(
            api_key="test-key",
            model="glm-4.6",
            provider_name="bigmodel",
            allow_mock=True,
            base_url="https://open.bigmodel.cn/api/paas/v4"
        )

        request_kwargs = client._build_request_kwargs(
            messages=[{"role": "user", "content": "hi"}],
            temperature=0.0,
            max_tokens=1200,
            response_format="json_object"
        )

        self.assertEqual({"type": "json_object"}, request_kwargs["response_format"])
        self.assertEqual("disabled", request_kwargs["extra_body"]["thinking"]["type"])


if __name__ == "__main__":
    unittest.main()
