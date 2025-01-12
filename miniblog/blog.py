from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
import markdown
from . import db
from .models import Article, Tag
from bleach import clean, linkifier

# Création du blueprint pour le blog
bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    """Page d'accueil du blog"""
    page = request.args.get('page', 1, type=int)
    articles = Article.query.order_by(Article.created_at.desc()).paginate(page=page, per_page=10)
    tags = Tag.query.all()
    return render_template('blog/index.html', articles=articles, tags=tags)

@bp.route('/tag/<tag_name>')
def tag_view(tag_name):
    """Affiche les articles pour un tag donné"""
    page = request.args.get('page', 1, type=int)
    tag = Tag.query.filter_by(name=tag_name).first_or_404()
    
    articles = Article.query\
        .join(Article.tags)\
        .filter(Tag.id == tag.id)\
        .order_by(Article.created_at.desc())\
        .paginate(page=page, per_page=5)
    
    return render_template('blog/tag.html', tag=tag, articles=articles)

@bp.route('/admin')
@login_required
def admin_dashboard():
    """Tableau de bord administrateur"""
    articles = Article.query.order_by(Article.created_at.desc()).all()
    return render_template('blog/admin/dashboard.html', articles=articles)

@bp.route('/admin/article/new', methods=('GET', 'POST'))
@login_required
def new_article():
    """Création d'un nouvel article"""
    if request.method == 'POST':
        title = request.form['title'].strip()
        content = request.form['content']
        tag_names = [tag.strip() for tag in request.form['tags'].split(',') if tag.strip()]
        
        if not title:
            flash('Le titre est requis.')
            return render_template('blog/admin/editor.html')
            
        article = Article(
            title=title,
            content=content
        )
        
        # Gestion des tags
        for tag_name in tag_names:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
            article.tags.append(tag)
        
        try:
            db.session.add(article)
            db.session.commit()
            flash('Article créé avec succès !', 'success')
            return redirect(url_for('blog.admin_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('Une erreur est survenue lors de la création de l\'article.', 'error')
            return render_template('blog/admin/editor.html')
    
    return render_template('blog/admin/editor.html')

@bp.route('/admin/article/<int:id>/edit', methods=('GET', 'POST'))
@login_required
def edit_article(id):
    """Modification d'un article"""
    article = Article.query.get_or_404(id)
    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        tag_names = request.form['tags'].split()
        
        if not title:
            flash('Le titre est requis.')
        else:
            article.title = title
            article.content = content
            
            # Mise à jour des tags
            article.tags.clear()
            for tag_name in tag_names:
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                article.tags.append(tag)
            
            db.session.commit()
            return redirect(url_for('blog.admin_dashboard'))
    
    return render_template('blog/admin/editor.html', article=article)

@bp.route('/admin/article/<int:id>/delete', methods=('POST',))
@login_required
def delete_article(id):
    """Suppression d'un article"""
    article = Article.query.get_or_404(id)
    db.session.delete(article)
    db.session.commit()
    flash('Article supprimé avec succès.')
    return redirect(url_for('blog.admin_dashboard'))

@bp.route('/preview', methods=['POST'])
@login_required
def preview():
    """Prévisualisation du contenu Markdown"""
    try:
        content = request.json.get('content', '')
        if not content:
            return jsonify({'html': '<p class="text-muted">Commencez à écrire pour voir la prévisualisation...</p>'})
        
        # Configuration sécurisée de Markdown
        md = markdown.Markdown(
            extensions=['fenced_code', 'tables', 'nl2br'],
            extension_configs={
                'fenced_code': {},
                'tables': {},
                'nl2br': {}
            },
            output_format='html5'
        )
        
        # Convertit le Markdown en HTML
        html = md.convert(content)
        
        # Liste des tags HTML autorisés
        allowed_tags = [
            'p', 'br', 'strong', 'em', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'ul', 'ol', 'li', 'blockquote', 'code', 'pre', 'hr', 'table',
            'thead', 'tbody', 'tr', 'th', 'td', 'a', 'img'
        ]
        
        # Liste des attributs HTML autorisés
        allowed_attrs = {
            '*': ['class'],
            'a': ['href', 'title', 'target'],
            'img': ['src', 'alt', 'title']
        }
        
        # Nettoie le HTML
        clean_html = clean(
            html,
            tags=allowed_tags,
            attributes=allowed_attrs,
            strip=True
        )
        
        # Convertit les URLs en liens cliquables
        linker = linkifier.Linker(callbacks=[])
        linked_html = linker.linkify(clean_html)
        
        return jsonify({'html': linked_html})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400
