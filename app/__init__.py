from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv
import os
from flask_migrate import Migrate


db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "devsecret")
    app.config['SESSION_PERMANENT'] = False
    app.config.from_object('config.Config')
    migrate = Migrate(app, db)
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    

    # Import models AFTER initializing db
    with app.app_context():
        from app import models
        db.create_all()

    # Register routes
    from app.routes import auth, dashboard, recipes, mealplan, shopping, ai, home
    app.register_blueprint(home.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(recipes.bp)
    app.register_blueprint(mealplan.bp)
    app.register_blueprint(shopping.bp)
    app.register_blueprint(ai.bp)
    from datetime import timedelta
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SECURE'] = False  # Set True if using HTTPS

    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=10)  # or 15, etc.
    app.permanent_session_lifetime = timedelta(minutes=10)
    

    return app
