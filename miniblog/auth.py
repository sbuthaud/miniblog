from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from .models import Admin
import secrets
import string
from datetime import datetime, timedelta

# Création du blueprint pour l'authentification
bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    """Gestion de la connexion"""
    # Initialisation du dictionnaire des tentatives échouées
    if not hasattr(login, 'failed_attempts'):
        login.failed_attempts = {}
        
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        error = None
        
        # Protection contre les attaques par force brute
        current_time = datetime.now()
        
        # Nettoie les anciennes tentatives
        login.failed_attempts = {ip: data for ip, data in login.failed_attempts.items() 
                               if current_time - data['last_attempt'] < timedelta(minutes=15)}
        
        client_ip = request.remote_addr
        if client_ip in login.failed_attempts:
            if login.failed_attempts[client_ip]['count'] >= 5:
                if current_time - login.failed_attempts[client_ip]['last_attempt'] < timedelta(minutes=15):
                    flash('Trop de tentatives échouées. Réessayez dans 15 minutes.')
                    return render_template('auth/login.html')
                else:
                    login.failed_attempts[client_ip]['count'] = 0
        
        admin = Admin.query.filter_by(username=username).first()
        
        if admin is None:
            error = 'Nom d\'utilisateur ou mot de passe incorrect.'
        elif not check_password_hash(admin.password_hash, password):
            error = 'Nom d\'utilisateur ou mot de passe incorrect.'
            
            # Incrémente le compteur d'échecs
            if client_ip not in login.failed_attempts:
                login.failed_attempts[client_ip] = {'count': 0, 'last_attempt': current_time}
            login.failed_attempts[client_ip]['count'] += 1
            login.failed_attempts[client_ip]['last_attempt'] = current_time
            
        if error is None:
            # Réinitialise le compteur d'échecs en cas de succès
            if client_ip in login.failed_attempts:
                del login.failed_attempts[client_ip]
                
            login_user(admin, remember=False)  # Désactive "Se souvenir de moi"
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('blog.admin_dashboard')
            return redirect(next_page)
            
        flash(error)
    
    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    """Gestion de la déconnexion"""
    logout_user()
    return redirect(url_for('blog.index'))

def init_admin(app):
    """Création du compte administrateur initial"""
    with app.app_context():
        # Vérifie si un admin existe déjà
        if not Admin.query.first():
            # Génère un mot de passe aléatoire sécurisé
            alphabet = string.ascii_letters + string.digits + string.punctuation
            password = ''.join(secrets.choice(alphabet) for i in range(16))
            
            admin = Admin(
                username='admin',
                password_hash=generate_password_hash(password, method='pbkdf2:sha256:600000')
            )
            db.session.add(admin)
            db.session.commit()
            print('Compte administrateur créé avec succès !')
            print(f'Nom d\'utilisateur : admin')
            print(f'Mot de passe généré : {password}')
            print('IMPORTANT : Notez ces informations et changez le mot de passe après la première connexion')
