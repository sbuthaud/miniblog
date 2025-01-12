from miniblog import create_app, db
from miniblog.models import User

def init_db():
    app = create_app()
    with app.app_context():
        # Création des tables
        db.create_all()
        
        # Création d'un utilisateur admin par défaut si nécessaire
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin')
            admin.set_password('admin123')  # Changez ce mot de passe en production !
            db.session.add(admin)
            db.session.commit()
            print("Utilisateur admin créé avec succès !")
        
        print("Base de données initialisée avec succès !")
