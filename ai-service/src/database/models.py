"""
Database models for the AI service.
"""

from src.database.connection import db
from datetime import datetime


class RiskCase(db.Model):
    """Risk case model."""
    __tablename__ = 'risk_case'
    
    id = db.Column(db.BigInteger, primary_key=True)
    biz_transaction_id = db.Column(db.String(64), unique=True, nullable=False)
    amount = db.Column(db.Numeric(18, 2), nullable=False)
    currency = db.Column(db.String(10), nullable=False)
    country = db.Column(db.String(10))
    device_risk = db.Column(db.String(20))
    user_label = db.Column(db.String(50))
    risk_features = db.Column(db.JSON, nullable=False)
    rule_engine_score = db.Column(db.Numeric(5, 2))
    triggered_rules = db.Column(db.JSON)
    risk_score = db.Column(db.Numeric(5, 2))
    risk_level = db.Column(db.String(20))
    risk_status = db.Column(db.String(30), nullable=False)
    ai_decision_id = db.Column(db.BigInteger)
    final_decision = db.Column(db.String(20))
    reviewer_id = db.Column(db.BigInteger)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime)
    version = db.Column(db.Integer, default=0)
    
    def to_dict(self):
        return {
            'id': self.id,
            'biz_transaction_id': self.biz_transaction_id,
            'amount': float(self.amount) if self.amount else None,
            'currency': self.currency,
            'country': self.country,
            'device_risk': self.device_risk,
            'user_label': self.user_label,
            'risk_features': self.risk_features,
            'rule_engine_score': float(self.rule_engine_score) if self.rule_engine_score else None,
            'triggered_rules': self.triggered_rules,
            'risk_score': float(self.risk_score) if self.risk_score else None,
            'risk_level': self.risk_level,
            'risk_status': self.risk_status,
            'ai_decision_id': self.ai_decision_id,
            'final_decision': self.final_decision,
            'reviewer_id': self.reviewer_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class AIDecisionRecord(db.Model):
    """AI decision record model."""
    __tablename__ = 'ai_decision_record'
    
    id = db.Column(db.BigInteger, primary_key=True)
    case_id = db.Column(db.BigInteger, nullable=False)
    prompt_version = db.Column(db.String(20), nullable=False)
    ai_decision = db.Column(db.String(20))
    ai_confidence = db.Column(db.Numeric(5, 2))
    ai_reasoning = db.Column(db.Text)
    similar_cases = db.Column(db.JSON)
    rule_query_result = db.Column(db.JSON)
    history_analysis = db.Column(db.JSON)
    override_flag = db.Column(db.Boolean, default=False)
    override_reason = db.Column(db.Text)
    final_decision = db.Column(db.String(20))
    retrieval_time_ms = db.Column(db.Integer)
    llm_call_time_ms = db.Column(db.Integer)
    total_time_ms = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime)
    version = db.Column(db.Integer, default=0)
    
    def to_dict(self):
        return {
            'id': self.id,
            'case_id': self.case_id,
            'prompt_version': self.prompt_version,
            'ai_decision': self.ai_decision,
            'ai_confidence': float(self.ai_confidence) if self.ai_confidence else None,
            'ai_reasoning': self.ai_reasoning,
            'similar_cases': self.similar_cases,
            'rule_query_result': self.rule_query_result,
            'history_analysis': self.history_analysis,
            'override_flag': self.override_flag,
            'override_reason': self.override_reason,
            'final_decision': self.final_decision,
            'retrieval_time_ms': self.retrieval_time_ms,
            'llm_call_time_ms': self.llm_call_time_ms,
            'total_time_ms': self.total_time_ms,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class KnowledgeDocument(db.Model):
    """Knowledge document model for vector storage."""
    __tablename__ = 'knowledge_document'
    
    id = db.Column(db.BigInteger, primary_key=True)
    doc_type = db.Column(db.String(50))
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    embedding = db.Column(db.JSON)  # Store as JSON for now, use pgvector in production
    meta = db.Column('metadata', db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'doc_type': self.doc_type,
            'title': self.title,
            'content': self.content,
            'metadata': self.meta,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class PromptTemplate(db.Model):
    """Prompt template model."""
    __tablename__ = 'prompt_template'
    
    id = db.Column(db.BigInteger, primary_key=True)
    version = db.Column(db.String(20), unique=True, nullable=False)
    system_prompt = db.Column(db.Text, nullable=False)
    user_prompt_template = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=False)
    avg_response_time_ms = db.Column(db.Integer)
    override_rate = db.Column(db.Numeric(5, 2))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime)
    version_num = db.Column(db.Integer, default=0)
    
    def to_dict(self):
        return {
            'id': self.id,
            'version': self.version,
            'system_prompt': self.system_prompt,
            'user_prompt_template': self.user_prompt_template,
            'description': self.description,
            'is_active': self.is_active,
            'avg_response_time_ms': self.avg_response_time_ms,
            'override_rate': float(self.override_rate) if self.override_rate else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class AIPromptLog(db.Model):
    """AI prompt log model for recording AI calls."""
    __tablename__ = 'ai_prompt_log'
    
    id = db.Column(db.BigInteger, primary_key=True)
    case_id = db.Column(db.BigInteger, nullable=False)
    ai_decision_id = db.Column(db.BigInteger)
    prompt_version = db.Column(db.String(20), nullable=False)
    system_prompt = db.Column(db.Text)
    user_prompt = db.Column(db.Text)
    llm_response = db.Column(db.Text)
    llm_model = db.Column(db.String(100))
    input_tokens = db.Column(db.Integer)
    output_tokens = db.Column(db.Integer)
    total_tokens = db.Column(db.Integer)
    latency_ms = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'case_id': self.case_id,
            'ai_decision_id': self.ai_decision_id,
            'prompt_version': self.prompt_version,
            'system_prompt': self.system_prompt,
            'user_prompt': self.user_prompt,
            'llm_response': self.llm_response,
            'llm_model': self.llm_model,
            'input_tokens': self.input_tokens,
            'output_tokens': self.output_tokens,
            'total_tokens': self.total_tokens,
            'latency_ms': self.latency_ms,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
