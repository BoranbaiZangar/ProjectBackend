from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required
from app.models import Character, Project
from app import db

character = Blueprint('character', __name__, url_prefix='/character')

@character.route('/<int:project_id>')
@login_required
def list_characters(project_id):
    project = Project.query.get_or_404(project_id)
    characters = Character.query.filter_by(project_id=project_id).all()
    return render_template('characters.html', characters=characters, project=project)

@character.route('/<int:project_id>/add', methods=['GET', 'POST'])
@login_required
def add_character(project_id):
    if request.method == 'POST':
        name = request.form.get('name')
        age = request.form.get('age')
        gender = request.form.get('gender')
        appearance = request.form.get('appearance')
        personality = request.form.get('personality')
        backstory = request.form.get('backstory')

        new_char = Character(
            name=name,
            age=age,
            gender=gender,
            appearance=appearance,
            personality=personality,
            backstory=backstory,
            project_id=project_id
        )
        db.session.add(new_char)
        db.session.commit()
        return redirect(url_for('character.list_characters', project_id=project_id))

    return render_template('add_character.html', project_id=project_id)

@character.route('/edit/<int:char_id>', methods=['GET', 'POST'])
@login_required
def edit_character(char_id):
    char = Character.query.get_or_404(char_id)
    if request.method == 'POST':
        char.name = request.form.get('name')
        char.age = request.form.get('age')
        char.gender = request.form.get('gender')
        char.appearance = request.form.get('appearance')
        char.personality = request.form.get('personality')
        char.backstory = request.form.get('backstory')

        db.session.commit()
        return redirect(url_for('character.list_characters', project_id=char.project_id))

    return render_template('edit_character.html', character=char)

@character.route('/delete/<int:char_id>')
@login_required
def delete_character(char_id):
    char = Character.query.get_or_404(char_id)
    project_id = char.project_id
    db.session.delete(char)
    db.session.commit()
    return redirect(url_for('character.list_characters', project_id=project_id))
