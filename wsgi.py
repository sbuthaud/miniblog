#!/usr/bin/env python3
from miniblog import create_app

application = create_app()
app = application  # Pour la compatibilité avec Gunicorn
