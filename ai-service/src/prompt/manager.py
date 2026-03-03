"""
Prompt template manager for managing different prompt versions.
"""

import logging
from typing import Dict, Any, Optional, List
from sqlalchemy import func

logger = logging.getLogger(__name__)


class PromptManager:
    """Manager for prompt templates."""
    
    def __init__(self, db_session):
        """
        Initialize prompt manager.
        
        Args:
            db_session: Database session
        """
        self.db_session = db_session
        self._cache = {}
    
    def get_active_prompt(self) -> Optional[Dict[str, str]]:
        """
        Get the currently active prompt template.
        
        Returns:
            Prompt template with system_prompt and user_prompt_template
        """
        try:
            from src.database.models import PromptTemplate
            
            # Try to get from cache first
            if 'active' in self._cache:
                return self._cache['active']
            
            # Query database
            template = self.db_session.query(PromptTemplate).filter_by(is_active=True).first()
            
            if template:
                prompt_dict = {
                    'version': template.version,
                    'system_prompt': template.system_prompt,
                    'user_prompt_template': template.user_prompt_template
                }
                self._cache['active'] = prompt_dict
                return prompt_dict
            
            logger.warning("No active prompt template found")
            return None
        except Exception as e:
            logger.error(f"Error getting active prompt: {str(e)}")
            return None
    
    def get_prompt_by_version(self, version: str) -> Optional[Dict[str, str]]:
        """
        Get prompt template by version.
        
        Args:
            version: Prompt version (e.g., 'v1', 'v2')
            
        Returns:
            Prompt template
        """
        try:
            from src.database.models import PromptTemplate
            
            # Try to get from cache first
            if version in self._cache:
                return self._cache[version]
            
            # Query database
            template = self.db_session.query(PromptTemplate).filter_by(version=version).first()
            
            if template:
                prompt_dict = {
                    'version': template.version,
                    'system_prompt': template.system_prompt,
                    'user_prompt_template': template.user_prompt_template
                }
                self._cache[version] = prompt_dict
                return prompt_dict
            
            logger.warning(f"Prompt template not found: {version}")
            return None
        except Exception as e:
            logger.error(f"Error getting prompt by version: {str(e)}")
            return None
    
    def get_all_prompts(self) -> List[Dict[str, Any]]:
        """
        Get all prompt templates.
        
        Returns:
            List of prompt templates
        """
        try:
            from src.database.models import PromptTemplate
            
            templates = self.db_session.query(PromptTemplate).all()
            
            return [
                {
                    'id': t.id,
                    'version': t.version,
                    'description': t.description,
                    'is_active': t.is_active,
                    'created_at': t.created_at.isoformat() if t.created_at else None
                }
                for t in templates
            ]
        except Exception as e:
            logger.error(f"Error getting all prompts: {str(e)}")
            return []
    
    def create_prompt(self, version: str, system_prompt: str, user_prompt_template: str, 
                     description: str = None) -> Optional[Dict[str, Any]]:
        """
        Create a new prompt template.
        
        Args:
            version: Prompt version
            system_prompt: System prompt text
            user_prompt_template: User prompt template
            description: Description of the prompt
            
        Returns:
            Created prompt template
        """
        try:
            from src.database.models import PromptTemplate
            
            # Check if version already exists
            existing = self.db_session.query(PromptTemplate).filter_by(version=version).first()
            if existing:
                raise ValueError(f"Prompt version already exists: {version}")
            
            # Create new template
            template = PromptTemplate(
                version=version,
                system_prompt=system_prompt,
                user_prompt_template=user_prompt_template,
                description=description,
                is_active=False
            )
            if self._uses_sqlite():
                template.id = self._next_id(PromptTemplate)
            
            self.db_session.add(template)
            self.db_session.commit()
            
            # Clear cache
            self._cache.clear()
            
            logger.info(f"Created prompt template: {version}")
            
            return {
                'id': template.id,
                'version': template.version,
                'description': template.description,
                'is_active': template.is_active
            }
        except Exception as e:
            logger.error(f"Error creating prompt: {str(e)}")
            self.db_session.rollback()
            return None
    
    def activate_prompt(self, version: str) -> bool:
        """
        Activate a prompt template.
        
        Args:
            version: Prompt version to activate
            
        Returns:
            True if successful
        """
        try:
            from src.database.models import PromptTemplate
            
            # Deactivate all other templates
            self.db_session.query(PromptTemplate).update({'is_active': False})
            
            # Activate the specified template
            template = self.db_session.query(PromptTemplate).filter_by(version=version).first()
            if template:
                template.is_active = True
                self.db_session.commit()
                
                # Clear cache
                self._cache.clear()
                
                logger.info(f"Activated prompt template: {version}")
                return True
            else:
                logger.warning(f"Prompt template not found: {version}")
                return False
        except Exception as e:
            logger.error(f"Error activating prompt: {str(e)}")
            self.db_session.rollback()
            return False
    
    def format_prompt(self, template_str: str, **kwargs) -> str:
        """
        Format prompt template with variables.
        
        Args:
            template_str: Template string with {variable} placeholders
            **kwargs: Variables to substitute
            
        Returns:
            Formatted prompt
        """
        try:
            return template_str.format(**kwargs)
        except KeyError as e:
            logger.error(f"Missing template variable: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error formatting prompt: {str(e)}")
            raise

    def ensure_default_prompts(self) -> None:
        """Ensure there is at least one active prompt template."""
        try:
            from src.database.models import PromptTemplate

            existing_count = self.db_session.query(PromptTemplate).count()
            if existing_count > 0:
                active = self.db_session.query(PromptTemplate).filter_by(is_active=True).first()
                if active is None:
                    first = self.db_session.query(PromptTemplate).order_by(PromptTemplate.id.asc()).first()
                    if first:
                        first.is_active = True
                        self.db_session.commit()
                return

            v1 = PromptTemplate(
                version='v1',
                system_prompt=(
                    "You are a senior risk analyst. You must provide a strict JSON response only."
                ),
                user_prompt_template=(
                    "Analyze this case and return JSON only with keys: "
                    "risk_level, confidence_score, key_risk_points, suggested_action, reasoning. "
                    "Case: amount={amount}, currency={currency}, country={country}, "
                    "device_risk={device_risk}, user_label={user_label}, "
                    "rule_score={rule_score}, triggered_rules={triggered_rules}, "
                    "similar_cases={similar_cases}, transaction_history={transaction_history}."
                ),
                description='Default prompt template',
                is_active=True
            )
            if self._uses_sqlite():
                v1.id = self._next_id(PromptTemplate)
            self.db_session.add(v1)
            self.db_session.commit()
            self._cache.clear()
            logger.info("Initialized default prompt template v1")
        except Exception as e:
            logger.error(f"Error ensuring default prompts: {str(e)}")
            self.db_session.rollback()

    def _uses_sqlite(self) -> bool:
        """Return True when current DB dialect is SQLite."""
        bind = self.db_session.get_bind()
        return bool(bind and bind.dialect and bind.dialect.name == 'sqlite')

    def _next_id(self, model) -> int:
        """Generate a numeric ID for SQLite where BIGINT PK is not auto-incrementing."""
        max_id = self.db_session.query(func.max(model.id)).scalar()
        return int(max_id or 0) + 1


# Global prompt manager instance
_prompt_manager = None


def get_prompt_manager(db_session) -> PromptManager:
    """Get or create prompt manager."""
    global _prompt_manager
    
    if _prompt_manager is None:
        _prompt_manager = PromptManager(db_session)
    
    return _prompt_manager
