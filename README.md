# MiniBlog

Un blog minimaliste créé avec Flask, permettant de publier et gérer des articles avec un éditeur Markdown.

## Fonctionnalités

- Interface d'administration sécurisée
- Éditeur d'articles avec prévisualisation Markdown en temps réel
- Gestion des tags pour catégoriser les articles
- Protection contre les attaques XSS et CSRF
- Interface responsive et moderne

## Installation

1. Clonez le repository :
```bash
git clone https://github.com/votre-username/miniblog.git
cd miniblog
```

2. Créez un environnement virtuel et activez-le :
```bash
python -m venv venv
source venv/bin/activate  # Sur Unix/macOS
# ou
venv\Scripts\activate  # Sur Windows
```

3. Installez les dépendances :
```bash
pip install -r requirements.txt
```

4. Initialisez la base de données :
```bash
flask init-db
```

5. Lancez l'application :
```bash
python run.py
```

L'application sera accessible à l'adresse : `http://localhost:5001`

## Configuration

- `FLASK_ENV` : Définit l'environnement ('development' ou 'production')
- `SECRET_KEY` : Clé secrète pour la sécurité (à définir en production)

## Sécurité

- Protection CSRF active
- Sanitization HTML avec Bleach
- Stockage sécurisé des mots de passe avec PBKDF2
- Protection contre les attaques par force brute

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
1. Fork le projet
2. Créer une branche pour votre fonctionnalité
3. Commiter vos changements
4. Pousser vers la branche
5. Ouvrir une Pull Request

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.
