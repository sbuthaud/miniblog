from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
import os
import markdown
from datetime import timedelta

# Initialisation de Flask et de la base de données
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app():
    # Création de l'application Flask
    app = Flask(__name__)
    
    # Détection de l'environnement
    env = os.environ.get('FLASK_ENV', 'development')
    is_development = env == 'development'
    
    # Configuration de base
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Configuration de sécurité adaptée à l'environnement
    app.config.update(
        SESSION_COOKIE_SECURE=not is_development,  # False en développement pour HTTP
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        PERMANENT_SESSION_LIFETIME=timedelta(minutes=30),
        REMEMBER_COOKIE_DURATION=timedelta(days=7),
        REMEMBER_COOKIE_SECURE=not is_development,  # False en développement pour HTTP
        REMEMBER_COOKIE_HTTPONLY=True,
        REMEMBER_COOKIE_SAMESITE='Lax',
        WTF_CSRF_TIME_LIMIT=None,  # Pas de limite de temps pour le token CSRF
        WTF_CSRF_CHECK_DEFAULT=True,  # Activer la vérification CSRF par défaut
        WTF_CSRF_SSL_STRICT=False  # Désactiver la vérification SSL stricte en développement
    )
    
    # Headers de sécurité
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # HSTS seulement en production
        if not is_development:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        # CSP plus permissif en développement
        if is_development:
            csp = "default-src 'self' 'unsafe-inline' 'unsafe-eval'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'"
        else:
            csp = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
        
        response.headers['Content-Security-Policy'] = csp
        return response

    # Initialisation des extensions
    db.init_app(app)
    csrf.init_app(app)
    
    # Configuration de Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
    
    @login_manager.user_loader
    def load_user(user_id):
        from .models import Admin
        return Admin.query.get(int(user_id))
    
    # Ajout du filtre Markdown
    @app.template_filter('markdown')
    def markdown_filter(text):
        return markdown.markdown(text)

    with app.app_context():
        # Création des tables de la base de données
        db.create_all()

        # Enregistrement des blueprints (routes)
        from .auth import bp as auth_bp
        from .blog import bp as blog_bp
        
        app.register_blueprint(auth_bp)
        app.register_blueprint(blog_bp)

        return app
