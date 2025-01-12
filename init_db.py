from miniblog import create_app, db
from miniblog.models import Admin, Article, Tag

def init_db():
    app = create_app()
    with app.app_context():
        # Création de toutes les tables
        db.create_all()
        print("Tables créées avec succès !")
        
        # Création d'un administrateur par défaut si nécessaire
        if not Admin.query.filter_by(username='admin').first():
            admin = Admin(username='admin')
            admin.set_password('admin123')  # Changez ce mot de passe en production !
            db.session.add(admin)
            db.session.commit()
            print("Administrateur créé avec succès !")
        
        print("Base de données initialisée avec succès !")

if __name__ == '__main__':
    init_db()
