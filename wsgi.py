#!/usr/bin/env python3
import os
import sys

# Ajout du répertoire racine au PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import de l'application
from miniblog import create_app

# Création de l'instance de l'application
application = create_app()

# Pour la compatibilité avec différents serveurs WSGI
app = application
