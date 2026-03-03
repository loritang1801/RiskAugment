import os
from datetime import timedelta


class Config:
    """Base configuration"""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = False
    TESTING = False
    
    # Database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # CORS
    CORS_ORIGINS = ['http://localhost:3000', 'http://localhost:8080']
    
    # Redis
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # LLM Configuration
    LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'openai')  # openai/openai_compatible/bigmodel/deepseek/minimax/anthropic
    LLM_MODEL = os.getenv('LLM_MODEL', 'gpt-4o-mini')
    LLM_BASE_URL = os.getenv('LLM_BASE_URL', '')
    LLM_API_KEY = os.getenv('LLM_API_KEY', '')
    LLM_TIMEOUT = int(os.getenv('LLM_TIMEOUT', 30))
    LLM_MAX_RETRIES = int(os.getenv('LLM_MAX_RETRIES', 0))
    
    # Embedding Configuration
    EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'BAAI/bge-large-zh-v1.5')
    EMBEDDING_DIMENSION = int(os.getenv('EMBEDDING_DIMENSION', 1024))
    
    # RAG Configuration
    RAG_TOP_K = int(os.getenv('RAG_TOP_K', 5))
    RAG_SIMILARITY_THRESHOLD = float(os.getenv('RAG_SIMILARITY_THRESHOLD', 0.7))

    # Upstream Tool Integrations (Agent hybrid mode)
    RULE_ENGINE_URL = os.getenv('RULE_ENGINE_URL', '')
    RULE_ENGINE_TOKEN = os.getenv('RULE_ENGINE_TOKEN', '')
    RULE_ENGINE_TIMEOUT_SECONDS = int(os.getenv('RULE_ENGINE_TIMEOUT_SECONDS', 5))
    TRANSACTION_HISTORY_URL = os.getenv('TRANSACTION_HISTORY_URL', '')
    TRANSACTION_HISTORY_TOKEN = os.getenv('TRANSACTION_HISTORY_TOKEN', '')
    TRANSACTION_HISTORY_TIMEOUT_SECONDS = int(os.getenv('TRANSACTION_HISTORY_TIMEOUT_SECONDS', 5))
    AGENT_TOOL_ALLOW_FALLBACK = os.getenv('AGENT_TOOL_ALLOW_FALLBACK', 'false').lower() == 'true'
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = True
    # Keep default aligned with backend dev profile and interview docs.
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://risk_control_user:risk_control_password@localhost:5433/risk_control_db'
    )


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    REDIS_URL = 'redis://localhost:6379/1'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SESSION_COOKIE_SECURE = True
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '').split(',')
