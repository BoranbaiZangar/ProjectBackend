from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from app.models import Project
from app import db

projects = Blueprint('projects', __name__)

@projects.route('/')
@login_required
def dashboard():
    user_projects = Project.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', projects=user_projects)

@projects.route('/create_project', methods=['POST'])
@login_required
def create_project():
    title = request.form.get('title')
    if title:
        new_project = Project(title=title, user_id=current_user.id)
        db.session.add(new_project)
        db.session.commit()
    return redirect(url_for('projects.dashboard'))

@projects.route('/delete_project/<int:id>')
@login_required
def delete_project(id):
    project = Project.query.get_or_404(id)
    if project.user_id == current_user.id:
        db.session.delete(project)
        db.session.commit()
    return redirect(url_for('projects.dashboard'))
