import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app(config_name='development'):
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # Configuration
    if config_name == 'production':
        from config import ProductionConfig
        app.config.from_object(ProductionConfig)
    elif config_name == 'testing':
        from config import TestingConfig
        app.config.from_object(TestingConfig)
    else:
        from config import DevelopmentConfig
        app.config.from_object(DevelopmentConfig)
    
    # CORS
    CORS(app, origins=app.config.get('CORS_ORIGINS', ['http://localhost:3000']))
    
    # Database initialization
    from src.database.connection import init_db, get_db_session
    init_db(app)
    
    # Initialize AI components
    from src.llm.client import get_default_llm_client
    from src.prompt.manager import get_prompt_manager
    from src.rag.retriever import Retriever
    from src.agent.agent import get_agent

    llm_client = get_default_llm_client()
    with app.app_context():
        db_session = get_db_session()
        prompt_manager = get_prompt_manager(db_session)
        prompt_manager.ensure_default_prompts()
        retriever = Retriever(db_session)
        ai_agent = get_agent(llm_client, prompt_manager, retriever)
    
    # Store in app config
    app.config['llm_client'] = llm_client
    app.config['prompt_manager'] = prompt_manager
    app.config['retriever'] = retriever
    app.config['ai_agent'] = ai_agent
    
    # Register blueprints
    from src.api.routes import api_bp
    from src.api.rag_routes import rag_bp
    from src.api.ai_routes import ai_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(rag_bp)
    app.register_blueprint(ai_bp)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({
            'status': 'error',
            'message': 'Resource not found'
        }), 404
    
    @app.errorhandler(500)
    def server_error(e):
        logger.error(f"Server error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({
            'status': 'healthy',
            'service': 'risk-control-ai-service',
            'version': '1.0.0'
        }), 200
    
    logger.info(f"Flask app created with config: {config_name}")
    logger.info("AI components initialized successfully")
    return app


if __name__ == '__main__':
    app = create_app(os.getenv('FLASK_ENV', 'development'))
    app.run(
        host=os.getenv('FLASK_HOST', '0.0.0.0'),
        port=int(os.getenv('FLASK_PORT', 5000)),
        debug=os.getenv('FLASK_DEBUG', False)
    )
