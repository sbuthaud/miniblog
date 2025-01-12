from miniblog import create_app
from miniblog.auth import init_admin

# Création de l'application
app = create_app()

# Initialisation du compte admin
init_admin(app)

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5001)
