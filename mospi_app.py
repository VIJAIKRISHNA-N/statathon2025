
"""
MoSPI Survey Data Processing System
AI-Enhanced Application for Automated Data Preparation, Estimation and Report Writing
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
import os
from datetime import datetime

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name='development'):
    """Create and configure Flask application"""
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///mospi_survey.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['REPORTS_FOLDER'] = 'reports'
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    # Import models (required for migrations)
    from app.models.survey import Survey
    from app.models.dataset import Dataset
    from app.models.cleaning_config import CleaningConfig
    from app.models.weight_config import WeightConfig
    from app.models.report import Report

    # Import and register blueprints
    from app.routes.api import api_bp
    from app.routes.data import data_bp
    from app.routes.cleaning import cleaning_bp
    from app.routes.weighting import weighting_bp
    from app.routes.reports import reports_bp

    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(data_bp, url_prefix='/api/data')
    app.register_blueprint(cleaning_bp, url_prefix='/api/cleaning')
    app.register_blueprint(weighting_bp, url_prefix='/api/weighting')
    app.register_blueprint(reports_bp, url_prefix='/api/reports')

    # Create database tables
    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
