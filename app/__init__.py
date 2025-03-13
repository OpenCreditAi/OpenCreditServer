from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from .config import Config

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    CORS(app)
    db.init_app(app)
    jwt.init_app(app)
    
    with app.app_context():
        from .routes.auth import auth_bp
        app.register_blueprint(auth_bp)
        
        # Import models to ensure they're registered with SQLAlchemy
        from .models.user import User
        
        # Create tables if they don't exist
        db.create_all()
    
    return app