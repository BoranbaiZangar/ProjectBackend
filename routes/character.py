import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required
from werkzeug.utils import secure_filename
from app.models import Character, Project
from app import db

character = Blueprint('character', __name__, url_prefix='/character')

# Разрешённые расширения
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_size(file):
    file.seek(0, os.SEEK_END)  # Перемещаем указатель в конец файла
    size = file.tell()  # Получаем размер файла
    file.seek(0)  # Восстанавливаем указатель на начало
    return size <= MAX_FILE_SIZE

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

        file = request.files.get('image')
        filename = None

        if file and file.filename != '':
            if not allowed_file(file.filename):
                flash('Допустимы только файлы .png, .jpg, .jpeg')
                return render_template('add_character.html', project_id=project_id)

            if not allowed_size(file):
                flash('Размер файла не должен превышать 10 МБ')
                return render_template('add_character.html', project_id=project_id)

            filename = secure_filename(file.filename)
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            file.save(os.path.join(upload_folder, filename))

        new_char = Character(
            name=name,
            age=age,
            gender=gender,
            appearance=appearance,
            personality=personality,
            backstory=backstory,
            image_filename=filename,  # Сохраняем имя файла изображения
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

        file = request.files.get('image')
        if file and file.filename != '':
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)

                # Удаление старого изображения
                if char.image_filename:
                    old_file_path = os.path.join(upload_folder, char.image_filename)
                    if os.path.exists(old_file_path):
                        os.remove(old_file_path)

                file.save(os.path.join(upload_folder, filename))
                char.image_filename = filename  # Обновление имени файла

            else:
                flash('Недопустимый формат изображения')

        db.session.commit()
        return redirect(url_for('character.list_characters', project_id=char.project_id))

    return render_template('edit_character.html', character=char)

@character.route('/delete/<int:char_id>')
@login_required
def delete_character(char_id):
    char = Character.query.get_or_404(char_id)
    project_id = char.project_id

    # Удаление изображения, если оно есть
    if char.image_filename:
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
        file_path = os.path.join(upload_folder, char.image_filename)
        if os.path.exists(file_path):
            os.remove(file_path)

    db.session.delete(char)
    db.session.commit()
    return redirect(url_for('character.list_characters', project_id=project_id))
