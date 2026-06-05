import os
from flask import Flask
from datetime import timedelta
import db as database

def create_app(config_name=None):
    """Application factory function."""
    app = Flask(__name__)

    # Configuration
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    if config_name == 'production':
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///expense_tracker.db')
        app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'change-me-in-production')
        app.config['SESSION_COOKIE_SECURE'] = True
        app.config['SESSION_COOKIE_HTTPONLY'] = True
        app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
        app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
    else:
        # Development configuration
        base_dir = os.path.abspath(os.path.dirname(__file__))
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{base_dir}/database/expense_tracker.db'
        app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
        app.config['SESSION_COOKIE_SECURE'] = False
        app.config['SESSION_COOKIE_HTTPONLY'] = True
        app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
        app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JSON_SORT_KEYS'] = False
    app.config['PERMANENT_SESSION'] = True

    # Initialize DB (SQLAlchemy engine + session)
    database.init_app(app)

    # Register error handlers
    register_error_handlers(app)

    # Root route
    @app.route('/')
    def index():
        from flask import redirect
        return redirect('/auth/')

    # Register blueprints
    with app.app_context():
        from routes.auth import auth_bp
        from routes.dashboard import dashboard_bp
        from routes.transactions import transactions_bp
        from routes.reports import reports_bp
        from routes.api import api_bp

        app.register_blueprint(auth_bp, url_prefix='/auth')
        app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
        app.register_blueprint(transactions_bp, url_prefix='/transactions')
        app.register_blueprint(reports_bp, url_prefix='/reports')
        app.register_blueprint(api_bp, url_prefix='/api')

        # Create tables using SQLAlchemy metadata
        database.create_all()

        # Initialize default categories
        init_default_categories()

    return app


def register_error_handlers(app):
    """Register error handlers for the application."""

    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Resource not found'}, 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {'error': 'Internal server error'}, 500

    @app.errorhandler(403)
    def forbidden(error):
        return {'error': 'Access forbidden'}, 403


def init_default_categories():
    """Initialize default categories for new users."""
    from models import Category, User

    expense_categories = ['Food', 'Transportation', 'Shopping', 'Bills', 'Healthcare', 'Entertainment', 'Education', 'Other']
    income_categories = ['Salary', 'Freelancing', 'Investments', 'Other']

    # This will be called for each new user during registration
    return {
        'expense': expense_categories,
        'income': income_categories
    }


app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
