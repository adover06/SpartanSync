from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app(config_class="app.config.Config"):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints
    from .auth import bp as auth_bp
    app.register_blueprint(auth_bp)
    
    from .main import bp as main_bp
    app.register_blueprint(main_bp)
    
    return app



