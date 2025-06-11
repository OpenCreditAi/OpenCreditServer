import os

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from .config import Config

db = SQLAlchemy()
jwt = JWTManager()
migrat = Migrate()


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    CORS(app)
    db.init_app(app)
    jwt.init_app(app)
    migrat.init_app(app, db)

    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    with app.app_context():
        from .routes.auth import auth_bp
        from .routes.file import file_bp
        from .routes.loan import loan_bp
        from .routes.offer import offer_bp

        app.register_blueprint(auth_bp)
        app.register_blueprint(loan_bp)
        app.register_blueprint(file_bp)
        app.register_blueprint(offer_bp)


        # Import models to ensure they're registered with SQLAlchemy
        from .models import File, Loan, User, offer
        
        # If you have other data with id's that are used in the static data then it will raise an error,
        # so the easy solution is to drop all active data
        if Config.ADD_STATIC_OFFERS:
            db.drop_all()
            
            
        # Create tables if they don't exist
        db.create_all()
        
        if Config.ADD_STATIC_OFFERS:
            from .populate_db import populate
            populate()


        # Schedule loan processing
        def scheduled_process_loans():
            with app.app_context():
                from .services.loan_service import LoanService
                from .models.loan import Loan
                loans = Loan.query.all()
                LoanService().process_loans(loans)

        # Scheduler
        scheduler = BackgroundScheduler()
        scheduler.add_job(scheduled_process_loans, 'cron', hour=0, minute=0)  # Midnight
        scheduler.start()

        # Ensure scheduler shuts down on exit
        import atexit
        atexit.register(lambda: scheduler.shutdown())


    return app
