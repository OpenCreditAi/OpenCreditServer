import os

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy

from .config import Config

db = SQLAlchemy()
jwt = JWTManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)
    db.init_app(app)
    jwt.init_app(app)

    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    with app.app_context():
        from .routes.auth import auth_bp
        from .routes.file import file_bp
        from .routes.loan import loan_bp

        app.register_blueprint(auth_bp)
        app.register_blueprint(loan_bp)
        app.register_blueprint(file_bp)

        # Import models to ensure they're registered with SQLAlchemy
        from .models import File, Loan, User

        # Create tables if they don't exist
        db.create_all()

    return app
