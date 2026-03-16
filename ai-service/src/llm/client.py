"""
LLM client for interacting with language models.
Supports OpenAI/Anthropic and OpenAI-compatible providers.
"""

import logging
import os
import threading
import time
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


OPENAI_COMPATIBLE_PROVIDERS = {
    'openai',
    'openai_compatible',
    'bigmodel',
    'deepseek',
    'minimax'
}

DEFAULT_BASE_URLS = {
    'bigmodel': 'https://open.bigmodel.cn/api/paas/v4',
    'deepseek': 'https://api.deepseek.com',
    'minimax': 'https://api.minimax.chat/v1'
}

DEFAULT_MODELS = {
    'openai': 'gpt-4o-mini',
    'openai_compatible': 'gpt-4o-mini',
    'bigmodel': 'glm-4.6',
    'deepseek': 'deepseek-chat',
    'minimax': 'MiniMax-Text-01',
    'anthropic': 'claude-3-5-sonnet-latest'
}


class LLMClient(ABC):
    """Abstract base class for LLM clients."""
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from prompt."""
        pass
    
    @abstractmethod
    def generate_with_context(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        """Generate text with system and user prompts."""
        pass


class _LocalRateLimiter:
    """In-process limiter to smooth burst traffic to upstream LLM provider."""

    def __init__(self, max_concurrency: int = 2, min_interval_ms: int = 300):
        self._semaphore = threading.BoundedSemaphore(max(1, max_concurrency))
        self._min_interval = max(0, min_interval_ms) / 1000.0
        self._lock = threading.Lock()
        self._last_call_ts = 0.0

    def __enter__(self):
        self._semaphore.acquire()
        with self._lock:
            now = time.monotonic()
            elapsed = now - self._last_call_ts
            wait_sec = self._min_interval - elapsed
            if wait_sec > 0:
                time.sleep(wait_sec)
            self._last_call_ts = time.monotonic()
        return self

    def __exit__(self, exc_type, exc, tb):
        self._semaphore.release()
        return False


def _is_rate_limit_error(err: Exception) -> bool:
    text = str(err).lower()
    return "rate limit" in text or "429" in text or "1302" in text


_GLOBAL_RATE_LIMITER = _LocalRateLimiter(
    max_concurrency=int(os.getenv("LLM_MAX_CONCURRENCY", "2")),
    min_interval_ms=int(os.getenv("LLM_MIN_INTERVAL_MS", "300")),
)


class OpenAIClient(LLMClient):
    """OpenAI-compatible API client."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = 'gpt-4o-mini',
        timeout: int = 30,
        allow_mock: bool = False,
        base_url: Optional[str] = None,
        provider_name: str = 'openai',
        max_retries: int = 0,
        rate_limit_retries: int = 2,
        rate_limit_backoff_ms: int = 800
    ):
        """
        Initialize OpenAI client.
        
        Args:
            api_key: API key
            model: Model name (gpt-4, gpt-3.5-turbo, etc.)
            timeout: Request timeout in seconds
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = model
        self.timeout = timeout
        self.allow_mock = allow_mock
        self.base_url = base_url or os.getenv('LLM_BASE_URL')
        self.provider = (provider_name or 'openai').lower()
        self.max_retries = max(0, max_retries)
        self.rate_limit_retries = max(0, rate_limit_retries)
        self.rate_limit_backoff_ms = max(100, rate_limit_backoff_ms)

        if not self.api_key and not self.allow_mock:
            logger.warning("LLM API key is missing; LLM calls will fail at runtime")

        try:
            from openai import OpenAI
            if self.api_key:
                self.client = OpenAI(
                    api_key=self.api_key,
                    timeout=self.timeout,
                    base_url=self.base_url,
                    max_retries=self.max_retries
                )
            else:
                self.client = None
        except ImportError:
            if self.allow_mock:
                logger.warning("openai package not installed, fallback to mock response")
                self.client = None
            else:
                raise RuntimeError("openai package is required when LLM_ALLOW_MOCK=false")
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from prompt."""
        if self.client is None:
            if not self.allow_mock:
                raise RuntimeError("OpenAI client unavailable and mock mode disabled")
            return self._mock_response(prompt)

        request_kwargs = self._build_request_kwargs(
            messages=[{"role": "user", "content": prompt}],
            temperature=kwargs.get('temperature', 0.7),
            max_tokens=kwargs.get('max_tokens', 1000),
            response_format=kwargs.get('response_format'),
            extra_body=kwargs.get('extra_body')
        )
        return self._request_with_rate_limit_retry(request_kwargs)
    
    def generate_with_context(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        """Generate text with system and user prompts."""
        if self.client is None:
            if not self.allow_mock:
                raise RuntimeError("OpenAI client unavailable and mock mode disabled")
            return self._mock_response(user_prompt)

        request_kwargs = self._build_request_kwargs(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=kwargs.get('temperature', 0.7),
            max_tokens=kwargs.get('max_tokens', 1000),
            response_format=kwargs.get('response_format'),
            extra_body=kwargs.get('extra_body')
        )
        return self._request_with_rate_limit_retry(request_kwargs)

    def _build_request_kwargs(
        self,
        messages: list,
        temperature: float,
        max_tokens: int,
        response_format: Optional[str] = None,
        extra_body: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        request_kwargs: Dict[str, Any] = {
            'model': self.model,
            'messages': messages,
            'temperature': temperature,
            'max_tokens': max_tokens
        }

        resolved_response_format = response_format or os.getenv('LLM_RESPONSE_FORMAT', 'json_object')
        if resolved_response_format == 'json_object':
            request_kwargs['response_format'] = {'type': 'json_object'}

        merged_extra_body = self._merge_extra_body(extra_body or {}, self._provider_extra_body())
        if merged_extra_body:
            request_kwargs['extra_body'] = merged_extra_body

        return request_kwargs

    def _provider_extra_body(self) -> Dict[str, Any]:
        extra_body: Dict[str, Any] = {}

        if self.provider == 'bigmodel':
            thinking_type = os.getenv('BIGMODEL_THINKING_TYPE', 'disabled').strip().lower()
            if thinking_type:
                extra_body['thinking'] = {'type': thinking_type}

        return extra_body

    def _merge_extra_body(self, base: Dict[str, Any], extra: Dict[str, Any]) -> Dict[str, Any]:
        merged = dict(base)
        for key, value in extra.items():
            if isinstance(value, dict) and isinstance(merged.get(key), dict):
                nested = dict(merged[key])
                nested.update(value)
                merged[key] = nested
            else:
                merged[key] = value
        return merged

    def _request_with_rate_limit_retry(self, request_kwargs: Dict[str, Any]) -> str:
        attempts = self.rate_limit_retries + 1
        last_error: Optional[Exception] = None
        for attempt in range(1, attempts + 1):
            try:
                with _GLOBAL_RATE_LIMITER:
                    response = self.client.chat.completions.create(**request_kwargs)
                content = response.choices[0].message.content
                return content or ""
            except Exception as e:
                last_error = e
                if _is_rate_limit_error(e) and attempt < attempts:
                    sleep_ms = self.rate_limit_backoff_ms * (2 ** (attempt - 1))
                    logger.warning(
                        "LLM rate-limit hit, retrying attempt %s/%s after %sms",
                        attempt + 1,
                        attempts,
                        sleep_ms
                    )
                    time.sleep(sleep_ms / 1000.0)
                    continue
                logger.error(f"Error generating text with rate-limit retry: {str(e)}")
                raise
        raise RuntimeError(f"LLM request failed after retries: {last_error}")
    
    def _mock_response(self, prompt: str) -> str:
        """Generate mock response for testing."""
        return """{
  "risk_level": "HIGH",
  "confidence_score": 0.85,
  "key_risk_points": [
    "High transaction amount",
    "New user account",
    "Suspicious device"
  ],
  "suggested_action": "REJECT",
  "reasoning": "Multiple risk factors detected"
}"""


class AnthropicClient(LLMClient):
    """Anthropic Claude API client."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = 'claude-3-5-sonnet-latest',
        timeout: int = 30,
        allow_mock: bool = False
    ):
        """
        Initialize Anthropic client.
        
        Args:
            api_key: Anthropic API key
            model: Model name
            timeout: Request timeout in seconds
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        self.model = model
        self.timeout = timeout
        self.allow_mock = allow_mock

        if not self.api_key and not self.allow_mock:
            logger.warning("ANTHROPIC_API_KEY is missing; LLM calls will fail at runtime")
        
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=self.api_key) if self.api_key else None
        except ImportError:
            if self.allow_mock:
                logger.warning("anthropic package not installed, fallback to mock response")
                self.client = None
            else:
                raise RuntimeError("anthropic package is required when LLM_ALLOW_MOCK=false")
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from prompt."""
        if self.client is None:
            if not self.allow_mock:
                raise RuntimeError("Anthropic client unavailable and mock mode disabled")
            return self._mock_response(prompt)
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=kwargs.get('max_tokens', 1000),
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.content[0].text
        except Exception as e:
            logger.error(f"Error generating text: {str(e)}")
            raise
    
    def generate_with_context(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        """Generate text with system and user prompts."""
        if self.client is None:
            if not self.allow_mock:
                raise RuntimeError("Anthropic client unavailable and mock mode disabled")
            return self._mock_response(user_prompt)
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=kwargs.get('max_tokens', 1000),
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            return response.content[0].text
        except Exception as e:
            logger.error(f"Error generating text with context: {str(e)}")
            raise
    
    def _mock_response(self, prompt: str) -> str:
        """Generate mock response for testing."""
        return """{
  "risk_level": "MEDIUM",
  "confidence_score": 0.75,
  "key_risk_points": [
    "Moderate transaction amount",
    "Existing user account",
    "Normal device"
  ],
  "suggested_action": "APPROVE",
  "reasoning": "Risk factors within acceptable range"
}"""


def get_llm_client(provider: str = 'openai', **kwargs) -> LLMClient:
    """
    Get LLM client based on provider.
    
    Args:
        provider: LLM provider
        **kwargs: Additional arguments for client initialization
        
    Returns:
        LLMClient instance
    """
    provider = provider.lower()

    if provider in OPENAI_COMPATIBLE_PROVIDERS:
        return OpenAIClient(**kwargs)
    elif provider == 'anthropic':
        return AnthropicClient(**kwargs)
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")


# Global LLM client instance
_llm_client = None


def get_default_llm_client() -> LLMClient:
    """Get or create default LLM client."""
    global _llm_client
    
    if _llm_client is None:
        provider = os.getenv('LLM_PROVIDER', 'openai').lower()
        if provider not in OPENAI_COMPATIBLE_PROVIDERS and provider != 'anthropic':
            logger.warning("Unknown LLM_PROVIDER=%s, fallback to openai_compatible", provider)
            provider = 'openai_compatible'

        model = os.getenv('LLM_MODEL', DEFAULT_MODELS.get(provider, 'gpt-4o-mini'))
        allow_mock = os.getenv('LLM_ALLOW_MOCK', 'false').lower() == 'true'
        timeout = int(os.getenv('LLM_TIMEOUT', 30))
        max_retries = int(os.getenv('LLM_MAX_RETRIES', 0))
        rate_limit_retries = int(os.getenv('LLM_RATE_LIMIT_RETRIES', 2))
        rate_limit_backoff_ms = int(os.getenv('LLM_RATE_LIMIT_BACKOFF_MS', 800))

        provider_key_map = {
            'openai': os.getenv('OPENAI_API_KEY'),
            'openai_compatible': os.getenv('OPENAI_COMPATIBLE_API_KEY'),
            'bigmodel': os.getenv('BIGMODEL_API_KEY') or os.getenv('ZHIPU_API_KEY'),
            'deepseek': os.getenv('DEEPSEEK_API_KEY'),
            'minimax': os.getenv('MINIMAX_API_KEY'),
            'anthropic': os.getenv('ANTHROPIC_API_KEY')
        }
        api_key = provider_key_map.get(provider) or os.getenv('LLM_API_KEY')

        base_url = os.getenv('LLM_BASE_URL')
        if not base_url and provider in DEFAULT_BASE_URLS:
            base_url = DEFAULT_BASE_URLS[provider]

        client_kwargs = {
            'api_key': api_key,
            'model': model,
            'timeout': timeout,
            'allow_mock': allow_mock
        }
        if provider in OPENAI_COMPATIBLE_PROVIDERS:
            client_kwargs['base_url'] = base_url
            client_kwargs['provider_name'] = provider
            client_kwargs['max_retries'] = max_retries
            client_kwargs['rate_limit_retries'] = rate_limit_retries
            client_kwargs['rate_limit_backoff_ms'] = rate_limit_backoff_ms

        _llm_client = get_llm_client(provider, **client_kwargs)
        logger.info(
            "LLM client initialized: provider=%s model=%s base_url=%s",
            provider,
            model,
            base_url or 'default'
        )
    
    return _llm_client
