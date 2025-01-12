import os
import sys

# Ajout du répertoire du projet au PYTHONPATH
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

from miniblog import create_app

app = create_app()
